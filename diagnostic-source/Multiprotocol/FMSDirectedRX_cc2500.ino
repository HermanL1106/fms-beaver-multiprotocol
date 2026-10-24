// Local FMS diagnostic: known-address normal scrambled 250K receive only.
// Based on the pinned project's CC2500/XN297 register configuration.
// No transmit strobe or payload transmission is performed here.
#if defined(FMS_DIRECT_CC2500) && defined(CC2500_INSTALLED)
#include "iface_xn297.h"
extern const uint8_t xn297_scramble[];
extern const uint16_t PROGMEM xn297_crc_xorout_scrambled[];

static uint8_t fms_cc_channel, fms_cc_option;
static uint32_t fms_cc_channel_at, fms_cc_stats_at, fms_cc_previous, fms_cc_sequence;
static bool fms_cc_have_previous, fms_cc_enabled;
static const uint8_t fms_cc_address[5]={0x7F,0xFF,0xFF,0xFF,0x7F};
#ifdef FMS_TRACK_RX
static const uint8_t fms_track_order[41]={2,75,26,54,4,74,40,8,73,45,6,72,30,50,10,70,34,12,36,69,38,13,68,58,14,66,18,28,52,62,20,61,29,60,22,46,24,44,56,42,76};
static uint32_t fms_track_previous, fms_track_run, fms_track_best, fms_track_total;
static bool fms_track_seen;
static uint8_t FMS_track_next(uint8_t channel)
{
	for(uint8_t i=0;i<41;i++)
		if(fms_track_order[i]==channel) return fms_track_order[(i+1)%41];
	return 22;
}
static uint8_t FMS_track_seed(uint8_t requested)
{
	for(uint8_t i=0;i<41;i++) if(fms_track_order[i]==requested) return requested;
	return 22; // Includes option=-1: acquisition seed, not scan in tracking build.
}
#endif

static void FMS_CC_restart()
{
	CC2500_Strobe(CC2500_SIDLE);
	CC2500_Strobe(CC2500_SFRX);
	CC2500_Strobe(CC2500_SRX);
}

static void FMS_CC_channel(uint8_t channel)
{
	fms_cc_channel=channel;
	CC2500_250K_RFChannel(channel);
	FMS_CC_restart();
	fms_cc_channel_at=micros();
	#ifndef FMS_TRACK_RX
		fms_cc_have_previous=false;
		debugln("CC_CH T_US=%lu C=%d",fms_cc_channel_at,channel);
	#endif
}

static void FMS_CC_init()
{
	BIND_DONE;
	fms_cc_enabled=false;
	NRF24L01_SetTxRxMode(TXRX_OFF);
	CC2500_Strobe(CC2500_SIDLE);
	#ifdef FMS_TRACK_RX
		debugln("FMS_DIAG_V4 TRACK41 RX_ONLY STRONG_RAW_RSSI=40..7F");
		fms_track_seen=false;
		fms_track_previous=fms_track_run=fms_track_best=fms_track_total=0;
	#else
		debugln("FMS_DIAG_V3 CC2500_DIRECT RX_ONLY ADDR=7FFFFFFF7F P16");
	#endif
	if(sub_protocol!=0 || RX_num!=5)
	{
		debugln("Select 250Kbps and receiver number 5; Auto disabled.");
		return;
	}
	XN297_Configure(XN297_CRCEN,XN297_SCRAMBLED,XN297_250K);
	// SetTXAddr establishes address length only on the CC2500 path; no TX.
	XN297_SetTXAddr(fms_cc_address,5);
	XN297_SetRXAddr(fms_cc_address,16);
	CC2500_SetTxRxMode(RX_EN);
	CC2500_WriteReg(CC2500_12_MDMCFG2,0x12); // GFSK, exact16-bit sync.
	CC2500_WriteReg(CC2500_06_PKTLEN,21); // remaining addr3 + payload16 + CRC2.
	CC2500_WriteReg(CC2500_0C_FSCTRL0,0); // option remains channel, NOT tuning.
	option_override=8; // RF channel option, matching XN297Dump interface.
	fms_cc_sequence=0;
	fms_cc_stats_at=micros();
	fms_cc_option=option;
	fms_cc_enabled=true;
	#ifdef FMS_TRACK_RX
		FMS_CC_channel(FMS_track_seed(option));
		debugln("TRACK_SEED C=%d OPTION=%d NO_SCAN",fms_cc_channel,(int8_t)option);
	#else
		FMS_CC_channel(option==0xFF ? 0 : (option<=84 ? option : 0));
	#endif
}

static bool FMS_CC_check(const uint8_t* fifo)
{
	if(fifo[0]!=0xB4 || fifo[1]!=0x15 || fifo[2]!=0xFA) return false;
	uint16_t check=0xB5D2;
	for(uint8_t i=0;i<21;i++)
	{
		uint8_t value=i==0 ? 0x9C : (i==1 ? 0x4E : fifo[i-2]);
		check^=(uint16_t)value<<8;
		for(uint8_t bit=0;bit<8;bit++) check=(check&0x8000) ? (check<<1)^0x1021 : check<<1;
	}
	check^=pgm_read_word(&xn297_crc_xorout_scrambled[18]);
	return (check>>8)==fifo[19] && (check&0xFF)==fifo[20];
}

static uint16_t FMS_CC_callback()
{
	if(!fms_cc_enabled) return 1000;
	if(sub_protocol!=0 || RX_num!=5)
	{
		CC2500_Strobe(CC2500_SIDLE);
		fms_cc_enabled=false;
		return 1000;
	}
	uint32_t now=micros();
	if(option!=fms_cc_option)
	{
		fms_cc_option=option;
		#ifdef FMS_TRACK_RX
			fms_track_seen=false;
			fms_track_run=0;
			FMS_CC_channel(FMS_track_seed(option));
		#else
			FMS_CC_channel(option==0xFF ? 0 : (option<=84 ? option : 0));
		#endif
	}
	#ifndef FMS_TRACK_RX
	else if(option==0xFF && (uint32_t)(now-fms_cc_channel_at)>=1000000UL)
		FMS_CC_channel(fms_cc_channel>=84 ? 0 : fms_cc_channel+1);
	#endif
	if((uint32_t)(now-fms_cc_stats_at)>=1000000UL)
	{
		fms_cc_stats_at=now;
		debugln("DIAG_SERIAL LONG=%lu BAD=%lu SIZE=%lu",diag_serial_long_count,diag_serial_bad_count,diag_serial_size_count);
		#ifdef FMS_TRACK_RX
			debugln("TRACK_STAT TOTAL=%lu RUN=%lu BEST=%lu C=%d",fms_track_total,fms_track_run,fms_track_best,fms_cc_channel);
		#endif
	}
	uint8_t available=CC2500_ReadReg(CC2500_3B_RXBYTES|CC2500_READ_BURST);
	if(available&0x80)
	{
		FMS_CC_restart();
		return 1000;
	}
	if(available>=23)
	{
		// FIFO has actual addr tail3, payload16, CRC2, RSSI and LQI.
		uint8_t fifo[23];
		CC2500_ReadData(fifo,sizeof(fifo));
		uint32_t received=micros();
		FMS_CC_restart(); // Re-arm before formatting USB output.
		uint32_t delta=fms_cc_have_previous ? received-fms_cc_previous : 0;
		fms_cc_previous=received;
		fms_cc_have_previous=true;
		bool valid=FMS_CC_check(fifo);
		#ifdef FMS_TRACK_RX
			if(valid && fifo[21]>=0x40 && fifo[21]<0x80)
			{
				uint8_t received_channel=fms_cc_channel;
				uint32_t gap=fms_track_seen ? received-fms_track_previous : 0;
				fms_track_run=fms_track_seen && gap>=3000 && gap<=30000 ? fms_track_run+1 : 1;
				if(fms_track_run>fms_track_best) fms_track_best=fms_track_run;
				fms_track_previous=received;
				fms_track_seen=true;
				fms_track_total++;
				FMS_CC_channel(FMS_track_next(received_channel)); // Retune before logging.
				debug("TR T=%lu C=%d D=%lu R=%lu F=",received,received_channel,gap,fms_track_run);
				for(uint8_t i=0;i<21;i++) debug("%02X",fifo[i]);
				debugln(" RSSI=%02X",fifo[21]);
			}
		#else
		debug("CC_RAW N=%lu T_US=%lu DT_US=%lu C=%d ",++fms_cc_sequence,received,delta,fms_cc_channel);
		debug("OK=%d SYNC=9C4E FIFO=",valid);
		for(uint8_t i=0;i<21;i++) debug(" %02X",fifo[i]);
		debugln(" RSSI=%02X LQI=%02X",fifo[21],fifo[22]);
		// Sync bytes are hardware-qualified, not bytes read from the FIFO.
		if(valid)
		{
			debug("CC_P16=");
			for(uint8_t i=0;i<16;i++) debug(" %02X",bit_reverse(fifo[3+i]^xn297_scramble[5+i]));
			debugln("");
		}
		#endif
	}
	return 1000;
}
#endif
