"""Host tests of actual bench callback and actual XN297 writer; no USB/RF access."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(__file__).parent
source = root / 'diagnostic-source/Multiprotocol'
emu = (source / 'XN297_EMU.ino').read_text()
tables = '\n'.join(re.findall(r'const uint(?:8|16)_t (?:PROGMEM )?xn297_\w+\[\] = \{.*?\};', emu, re.S))
writer = emu[emu.index('static void __attribute__((unused)) XN297_WritePayload('):emu.index('static void __attribute__((unused)) XN297_WriteEnhancedPayload(')]
bench = (source / 'FMSBenchTX_cc2500.ino').read_text().replace('#include "iface_xn297.h"', '')
prefix = r'''
#include <cstdint>
#include <cstring>
#include <cassert>
#include <cstdio>
#define FMS_BENCH_TX
#define PROGMEM
#define pgm_read_word(p) (*(p))
#define BIND_DONE ((void)0)
#define debugln(...) ((void)0)
#define debug(...) ((void)0)
#define IS_INPUT_SIGNAL_on input_live
#define CH16 15
#define CH7 6
#define CH5 4
#define CH8 7
#define THROTTLE 2
#define AILERON 0
#define ELEVATOR 1
#define RUDDER 3
#include "FMSBenchCore.h"
enum { TXRX_OFF,TX_EN,CC2500_SIDLE,CC2500_0C_FSCTRL0,CC2500_3E_PATABLE,CC2500_RANGE_POWER };
const bool XN297_CRCEN=true, XN297_SCRAMBLED=true, XN297_250K=true, XN297_NRF=false;
uint8_t option=2,sub_protocol=0,RX_num=5,option_override,hopping_frequency[50];
uint16_t Channel_data[16],crc;
bool input_live=true,xn297_rf=true,xn297_scramble_enabled=true,xn297_crc=true;
uint8_t xn297_addr_len=5,xn297_tx_addr[5]={0x7F,0xFF,0xFF,0xFF,0x7F};
uint32_t clock_ms=0,transmissions=0;
uint8_t wire[32],wire_len,current_hop;
uint32_t millis() {return clock_ms;}
uint8_t bit_reverse(uint8_t x) {uint8_t y=0;for(int i=0;i<8;i++){y=(y<<1)|(x&1);x>>=1;}return y;}
void crc16_update(uint8_t a,uint8_t bits) {crc^=uint16_t(a)<<8;while(bits--)crc=(crc&0x8000)?(crc<<1)^0x1021:crc<<1;}
void NRF24L01_SetTxRxMode(int) {}
void CC2500_Strobe(int) {}
void CC2500_SetTxRxMode(int) {}
void CC2500_WriteReg(int,int) {}
void CC2500_250K_HoppingCalib(int) {}
void CC2500_250K_Hopping(uint8_t index) {current_hop=hopping_frequency[index];}
void XN297_Configure(bool,bool,bool) {}
void XN297_SetTXAddr(const uint8_t* a,uint8_t n) {memcpy(xn297_tx_addr,a,n);xn297_addr_len=n;}
void XN297_SetTxRxMode(int) {}
void XN297_SendPayload(uint8_t* p,uint8_t n) {memcpy(wire,p,n);wire_len=n;transmissions++;}
'''
main = r'''
uint16_t field(const uint8_t* p,int i) {return p[2+i]|(((p[10+i/2]>>(4*(i%2)))&15)<<8);}
int main() {
 uint8_t p[16];
 for(uint16_t raw=0;raw<2048;raw++) {
   FMS_bench_pack(p,raw,2047-raw,raw,4095);
   assert(field(p,2)==1989 && field(p,4)==2000 && field(p,5)==1500 && field(p,6)==1500 && field(p,7)==4095);
   assert(field(p,0)>=1000 && field(p,0)<=2000);
   assert(field(p,3)==3000-FMS_bench_scale(raw));
   FMS_bench_pack(p,1024,1024,1024,1232,205,raw);
   assert(field(p,4)==(raw<600?1000:(raw>1400?2000:1500)));
   assert(field(p,0)==1500 && field(p,1)==1500 && field(p,2)==1989 && field(p,3)==1500);
   assert(field(p,6)==1500 && field(p,7)==1232);
 }
 for(int opt=0;opt<256;opt++) for(int ch=0;ch<2048;ch++)
   assert(FMS_bench_request(opt,ch,0,5)==(opt==42 && ch>1800));
 for(int button=0;button<2048;button++) {
   FMS_bench_pack(p,1024,1024,1024,4092,button);
   assert(field(p,6)==(button>1800?2000:1500));
   assert(field(p,2)==1989 && field(p,7)==4092);
 }
 assert(!FMS_bench_request(42,2047,1,5) && !FMS_bench_request(42,2047,0,4));
 for(auto &c:Channel_data)c=1024;
 option=42;Channel_data[15]=2047;FMS_Bench_init();FMS_Bench_callback();assert(transmissions==0);
 Channel_data[15]=0;FMS_Bench_callback();assert(transmissions==0);
 Channel_data[15]=2047;FMS_Bench_callback();assert(transmissions==1 && current_hop==2 && wire_len==23);
 for(int i=1;i<41;i++) {clock_ms+=9;FMS_Bench_callback();assert(current_hop==fms_bench_hops[i]);}
 clock_ms+=9;FMS_Bench_callback();assert(current_hop==2);
 while(clock_ms<30010) {clock_ms+=9;FMS_Bench_callback();}
 uint32_t total=transmissions;assert(!fms_bench_active);
 for(int i=0;i<10;i++) {clock_ms+=9;FMS_Bench_callback();} assert(transmissions==total);
 Channel_data[15]=0;FMS_Bench_callback();Channel_data[15]=2047;FMS_Bench_callback();assert(transmissions==total+1);
 clock_ms+=101;FMS_Bench_callback();assert(transmissions==total+1 && !fms_bench_active);
 clock_ms+=9;FMS_Bench_callback();assert(transmissions==total+1);
 Channel_data[15]=0;FMS_Bench_callback();Channel_data[15]=2047;FMS_Bench_callback();assert(transmissions==total+2);
 input_live=false;FMS_Bench_callback();assert(!fms_bench_active && transmissions==total+2);
 // Timer wrap must not bypass the30s lease or trigger a false input gap.
 input_live=true;clock_ms=0xfffff000u;option=42;Channel_data[15]=0;
 FMS_Bench_init();FMS_Bench_callback();Channel_data[15]=2047;FMS_Bench_callback();
 assert(fms_bench_active);uint32_t wrap_start=clock_ms;
 while(uint32_t(clock_ms-wrap_start)<30010u) {clock_ms+=9;FMS_Bench_callback();}
 assert(!fms_bench_active);uint32_t after_wrap=transmissions;
 for(int i=0;i<20;i++) {clock_ms+=9;FMS_Bench_callback();}
 assert(transmissions==after_wrap);
 // Check actual callback, not only request helper, for each invalid option.
 for(int opt=0;opt<256;opt++) {
   if(opt==42)continue;
   option=opt;Channel_data[15]=0;FMS_Bench_init();FMS_Bench_callback();
   Channel_data[15]=2047;FMS_Bench_callback();assert(transmissions==after_wrap);
 }
 puts("PASS: clock-wrap lease expiry and actual-callback invalid-option inhibition");
 FMSMotorGate gate;
 assert(!FMS_motor_step(gate,true,1843,204));
 assert(!FMS_motor_step(gate,true,205,204));
 assert(!FMS_motor_step(gate,true,1843,1024));
 assert(!FMS_motor_step(gate,true,1843,204)); // Must turn switch OFF before retry.
 assert(!FMS_motor_step(gate,true,205,204));
 assert(FMS_motor_step(gate,true,1843,204));
 assert(FMS_motor_step(gate,true,1843,1844));
 assert(!FMS_motor_step(gate,true,205,1844));
 assert(!FMS_motor_step(gate,false,1843,204));
 assert(!FMS_motor_step(gate,true,1843,204));
 for(uint16_t raw=0;raw<2048;raw++) {
   assert(FMS_motor_value(raw,false)==1989);
   assert(FMS_motor_value(raw,true)>=1000 && FMS_motor_value(raw,true)<=1989);
 }
 assert(FMS_motor_value(208,true)==1989 && FMS_motor_value(1844,true)==1000);
 puts("PASS: independent motor gate, low-throttle interlock, OFF/ON retry, inverse throttle range");
 puts("PASS: throttle lock, full input range, arm gates, hop order, timeout, input-gap disarm");
}
'''
# Verify the actual firmware writer reproduces real captured wire bytes.
checks = []
for log in (root / 'captures').glob('serial-*.log'):
    for match in re.finditer(r'TR[^\n]*? F=([0-9A-F]{42})', log.read_text(errors='replace')):
        fifo = bytes.fromhex(match[1])
        expected = bytes.fromhex('9C4E') + fifo
        # Derive the payload using independently expressed bit reversal and whitening.
        table = re.search(r'xn297_scramble\[\].*?\{(.*?)\}', emu, re.S)[1]
        scramble = bytes(int(v,16) for v in re.findall('0x[0-9A-Fa-f]+',table))
        payload = bytes(int(f'{v ^ scramble[i+5]:08b}'[::-1],2) for i,v in enumerate(fifo[3:19]))
        checks.append((payload,expected))
        if len(checks)>=128: break
    if len(checks)>=128: break
assert len(checks)==128
vectors = []
for p,w in checks:
    vectors.append('{' + '{'+','.join(map(str,p))+'},'+'{'+','.join(map(str,w))+'}' + '}')
extra = 'struct Vec {uint8_t p[16];uint8_t w[23];}; Vec vectors[]={' + ','.join(vectors) + '};\n'
extra += 'for(auto &v:vectors) {XN297_WritePayload(v.p,16);assert(wire_len==23 && !memcmp(wire,v.w,23));} transmissions=0;\n'
main = main.replace('int main() {', 'int main() {'+extra)
if '--monitor' in sys.argv:
    prefix += '\n#define FMS_BENCH_INPUT_ONLY\n'
    main = '''
int main() {
 FMS_Bench_init();
 for(int opt=0;opt<256;opt++) for(int ch=0;ch<2048;ch++) {
   option=opt;Channel_data[15]=ch;clock_ms++;FMS_Bench_callback();
 }
 assert(transmissions==0 && !fms_bench_active);
 puts("PASS: input-only actual callback never transmits across all option/CH16 combinations");
}
'''
if '--motor' in sys.argv:
    prefix += '\n#define FMS_BENCH_MOTOR\n'
    motor_test = r'''
 input_live=true;option=42;Channel_data[15]=205;Channel_data[7]=205;Channel_data[2]=208;
 FMS_Bench_init();FMS_Bench_callback();Channel_data[15]=1843;FMS_Bench_callback();
 assert(fms_bench_active && !fms_motor_gate.enabled);
 clock_ms+=9;Channel_data[2]=1024;Channel_data[7]=1843;FMS_Bench_callback();assert(!fms_motor_gate.enabled);
 clock_ms+=9;Channel_data[2]=208;FMS_Bench_callback();assert(!fms_motor_gate.enabled);
 clock_ms+=9;Channel_data[7]=205;FMS_Bench_callback();
 clock_ms+=9;Channel_data[7]=1843;FMS_Bench_callback();assert(fms_motor_gate.enabled);
 clock_ms+=9;Channel_data[2]=1844;FMS_Bench_callback();
 uint16_t actual_thr=bit_reverse(wire[9]^xn297_scramble[9])|((bit_reverse(wire[16]^xn297_scramble[16])&15)<<8);
 assert(actual_thr==1000);
 clock_ms+=9;Channel_data[7]=205;FMS_Bench_callback();
 actual_thr=bit_reverse(wire[9]^xn297_scramble[9])|((bit_reverse(wire[16]^xn297_scramble[16])&15)<<8);
 assert(actual_thr==1989 && !fms_motor_gate.enabled);
 puts("PASS: actual callback motor enable/cut reflected in emitted wire payload");
'''
    main = main.replace(' puts("PASS: throttle lock, full input range, arm gates, hop order, timeout, input-gap disarm");', motor_test+' puts("PASS: bench callback regression");')
if '--continuous' in sys.argv:
    prefix += '\n#define FMS_BENCH_MOTOR\n#define FMS_CONTINUOUS\n'
    main = r'''
int main() {
 for(auto &c:Channel_data)c=1024;
 option=42;Channel_data[15]=205;Channel_data[7]=205;Channel_data[2]=208;
 input_live=true;clock_ms=0xfffff000u;
 FMS_Bench_init();FMS_Bench_callback();assert(transmissions==0);
 Channel_data[15]=1843;FMS_Bench_callback();assert(transmissions==1);
 uint32_t started=clock_ms;
 while(uint32_t(clock_ms-started)<600000u) {
   clock_ms+=9;FMS_Bench_callback();
   assert(fms_bench_active && !fms_motor_gate.enabled);
 }
 assert(transmissions>60000);
 Channel_data[7]=1843;clock_ms+=9;FMS_Bench_callback();assert(fms_motor_gate.enabled);
 Channel_data[2]=1024;clock_ms+=9;FMS_Bench_callback();
 uint32_t last_tx=transmissions;
 Channel_data[15]=205;clock_ms+=9;FMS_Bench_callback();
 assert(!fms_bench_active && !fms_motor_gate.enabled && transmissions==last_tx);
 Channel_data[15]=1843;clock_ms+=9;FMS_Bench_callback();assert(fms_bench_active && !fms_motor_gate.enabled);
 clock_ms+=101;FMS_Bench_callback();assert(!fms_bench_active);
 last_tx=transmissions;clock_ms+=9;FMS_Bench_callback();assert(transmissions==last_tx);
 puts("PASS: continuous actual callback10min across clock wrap; separate motor gate, SA cutoff, no auto-resume after input gap");
}
'''
if '--release' in sys.argv:
    assert '--continuous' in sys.argv, 'Release must use continuous motor-gated tests'
    prefix += '\n#define FMS_RELEASE\n#define FMSBEAVER_CC2500_INO\n'
    bench += (source / 'FMSBeaver_cc2500.ino').read_text()
    main = main.replace('FMS_Bench_init()', 'FMSBeaver_init()').replace('FMS_Bench_callback()', 'FMSBeaver_callback()')
    main = main.replace('assert(transmissions==1);', 'assert(transmissions==1 && option_override==1);')
    release_checks = r'''
 input_live=true;option=0;Channel_data[15]=1843;
 FMSBeaver_init();FMSBeaver_callback();uint32_t before=transmissions;
 option=42;FMSBeaver_callback();assert(transmissions==before);
 Channel_data[15]=205;FMSBeaver_callback();Channel_data[15]=1843;
 FMSBeaver_callback();assert(transmissions==before+1);
 for(int profile=0;profile<64;profile++) if(profile!=5) {
   RX_num=profile;FMSBeaver_init();Channel_data[15]=205;
   FMSBeaver_callback();Channel_data[15]=1843;before=transmissions;
   FMSBeaver_callback();assert(transmissions==before);
   RX_num=5;FMSBeaver_callback();assert(transmissions==before);
 }
 puts("PASS: release entry, option metadata, profile rejection, no menu-change arming");
'''
    main = main.replace(' puts("PASS: continuous actual callback', release_checks+' puts("PASS: continuous actual callback')
host_build = tempfile.TemporaryDirectory(prefix='fms-bench-test-')
binary = Path(host_build.name) / 'bench-host-test'
subprocess.run(['clang++','-std=c++11','-fsanitize=address,undefined','-O1','-g','-I',str(source),'-x','c++','-','-o',str(binary)],input=prefix+tables+writer+bench+main,text=True,check=True)
subprocess.run([str(binary)],check=True)
host_build.cleanup()
if '--monitor' not in sys.argv and '--continuous' not in sys.argv:
    print('PASS: actual XN297 writer reproduces 128 captured address+payload+CRC vectors')
