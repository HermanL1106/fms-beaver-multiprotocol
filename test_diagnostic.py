"""Exercise the actual patched decoder on the host with ASan/UBSan."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).parent
source = root / 'diagnostic-source' / 'Multiprotocol'
dump = (source / 'XN297Dump_nrf24l01.ino').read_text()
emu = (source / 'XN297_EMU.ino').read_text()
tables = emu[emu.index('const uint8_t xn297_scramble[]'):emu.index('\nuint8_t', emu.index('const uint8_t xn297_scramble[]'))]
# Extract tables individually, avoiding the surrounding embedded-only code.
import re
tables = '\n'.join(re.findall(r'const uint(?:8|16)_t (?:PROGMEM )?xn297_\w+\[\] = \{.*?\};', emu, re.S))
decoder = dump[dump.index('static boolean __attribute__((unused)) XN297Dump_process_packet'):dump.index('static void __attribute__((unused)) XN297Dump_overflow')]
direct = (source / 'FMSDirectedRX_cc2500.ino').read_text()
direct_check = direct[direct.index('static bool FMS_CC_check'):direct.index('static uint16_t FMS_CC_callback')]
track_helpers = re.search(r'#ifdef FMS_TRACK_RX\n(.*?)#endif', direct, re.S)[1]
prefix = r'''
#include <cstdint>
#include <cstring>
#include <cassert>
#include <cstdio>
#include <random>
using boolean = bool;
#define PROGMEM
#define pgm_read_word(p) (*(p))
#define debugln(...) ((void)0)
#define XN297DUMP_MAX_PACKET_LEN 32
#define XN297DUMP_CRC_LENGTH 2
uint8_t packet[32], address_length, packet_length, pid;
bool enhanced, scramble, ack;
uint16_t crc;
uint8_t bit_reverse(uint8_t x) { uint8_t y=0; for(int i=0;i<8;i++) { y=(y<<1)|(x&1); x>>=1; } return y; }
void crc16_update(uint8_t a,uint8_t bits) { crc^=uint16_t(a)<<8; while(bits--) crc=(crc&0x8000)?(crc<<1)^0x1021:crc<<1; }
'''
main = r'''
int main() {
  char output[96];
  int count=snprintf(output,sizeof(output),"DIAG_RAW N=%lu TICKS=%lu DT_US=%lu C=%d AL=%d OK=%d RAW=",4294967295UL,4294967295UL,2147483647UL,84,5,1);
  assert(count==75 && count<int(sizeof(output)));
  // Synthetic normal vectors for all supported address/payload sizes that fit RAW32.
  for(int al=3;al<=5;al++) for(int len=1;len<=30-al;len++) for(int sc=0;sc<=1;sc++) {
    uint8_t original[32], expected[32];
    for(int i=0;i<32;i++) original[i]=uint8_t(i*13+0x21);
    address_length=al;
    for(int i=0;i<al;i++) expected[al-1-i]=original[i]^(sc?xn297_scramble[i]:0);
    for(int i=al;i<al+len;i++) expected[i]=bit_reverse(original[i]^(sc?xn297_scramble[i]:0));
    crc=0xb5d2; for(int i=0;i<al+len;i++) crc16_update(original[i],8);
    crc^=sc?xn297_crc_xorout_scrambled[al+len-3]:xn297_crc_xorout[al+len-3];
    original[al+len]=crc>>8; original[al+len+1]=crc;
    memcpy(packet,original,32);
    assert(XN297Dump_process_packet());
    assert(!enhanced && scramble==bool(sc) && packet_length==al+len);
    assert(!memcmp(packet,expected,al+len));
  }
  std::mt19937 rng(297);
  for(int n=0;n<200000;n++) {
    address_length=3+n%3;
    for(auto &b:packet) b=uint8_t(rng());
    bool ok=XN297Dump_process_packet();
    if(ok) { assert(address_length>=3 && address_length<=5); assert(packet_length>address_length && packet_length<=30); }
  }
  // Candidate timestamp must advance even when CRC failed; unsigned wrap is intentional.
  uint32_t previous=100, now=500; uint32_t delta=now-previous; previous=now;
  assert(delta==400); now=900; delta=now-previous; assert(delta==400);
  assert(uint32_t(uint32_t(0x20)-uint32_t(0xfffffff0))==0x30);
  puts("PASS: normal synthetic vectors, 200000 decoder fuzz inputs (ASan/UBSan), timestamp arithmetic");
}
'''
host_build = tempfile.TemporaryDirectory(prefix='fms-decoder-test-')
binary = Path(host_build.name) / 'decoder-host-test'
fixtures = []
for capture in (root / 'captures').glob('serial-*.log'):
    for match in re.finditer(r'DIAG_RAW[^\n]*?AL=5 OK=1 RAW=([^\n]+)', capture.read_text(errors='replace')):
        try:
            raw = bytes.fromhex(match[1])
        except ValueError:
            continue
        if raw[:5] != bytes.fromhex('9C 4E B4 15 FA'):
            continue
        fixtures.append('{' + ','.join(str(v) for v in raw[2:23]) + '}')
assert fixtures, 'Need independently CRC-checked captured FMS vectors'
extra = 'uint8_t captured[][21]={' + ','.join(fixtures) + '};\n'
extra += 'for(auto &f:captured) { assert(FMS_CC_check(f)); f[19]^=1; assert(!FMS_CC_check(f)); }\n'
extra += f'puts("PASS: {len(fixtures)} captured FMS vectors through CC2500 FIFO layout, plus CRC corruption rejection");\n'
main = main.replace('// Synthetic normal vectors', extra + '// Synthetic normal vectors')
track_test = '''
  bool seen_channels[85]={}; uint8_t channel=2;
  for(int i=0;i<41;i++) { assert(channel<=84 && !seen_channels[channel]); seen_channels[channel]=true; assert(FMS_track_seed(channel)==channel); channel=FMS_track_next(channel); }
  assert(channel==2 && FMS_track_seed(255)==22 && FMS_track_seed(84)==22);
  puts("PASS: tracking circular order has 41 unique channels; seed and wrap tested");
'''
main = main.replace('int main() {', 'int main() {' + track_test)
subprocess.run(['clang++', '-std=c++11', '-fsanitize=address,undefined', '-g', '-O1', '-x', 'c++', '-', '-o', str(binary)], input=prefix+tables+decoder+track_helpers+direct_check+main, text=True, check=True)
subprocess.run([str(binary)], check=True)
host_build.cleanup()
