// Experimental ground-test transmitter. NOT flight firmware.
// Built only with -DFMS_BUILD_BENCH; default build remains receive-only.
#ifdef FMS_BENCH_TX
#include "iface_xn297.h"
#include "FMSBenchCore.h"

static bool fms_bench_active, fms_bench_seen_disarm;
static uint32_t fms_bench_started, fms_bench_stats;
static uint32_t fms_bench_last_callback;
static uint16_t fms_bench_rolling;
static uint8_t fms_bench_index;
#ifdef FMS_BENCH_MOTOR
static FMSMotorGate fms_motor_gate;
#endif

static void FMS_Bench_stop()
{
	CC2500_Strobe(CC2500_SIDLE);
	CC2500_SetTxRxMode(TXRX_OFF);
	fms_bench_active=false;
	#ifdef FMS_BENCH_MOTOR
		FMS_motor_step(fms_motor_gate,false,0,0);
	#endif
}

static void FMS_Bench_init()
{
	BIND_DONE;
	NRF24L01_SetTxRxMode(TXRX_OFF);
	FMS_Bench_stop();
	fms_bench_seen_disarm=false;
	fms_bench_last_callback=millis();
	#ifdef FMS_RELEASE
		option_override=1; // Explicit enable option, not RF channel/frequency tune.
	#else
		option_override=8;
	#endif
	#ifdef FMS_BENCH_INPUT_ONLY
		debugln("FMS_INPUT_MONITOR RF_DISABLED: option and CH16 cannot arm TX");
	#endif
	#if defined(FMS_RELEASE)
		debugln("FMS_BEAVER_0.1.0_RC1 PRIVATE125 CAPTURED_PROFILE5 RANGE_POWER");
	#elif defined(FMS_CONTINUOUS)
		debugln("FMS_CONTROL_V6_CONTINUOUS MOTOR_GATED GROUND_VALIDATION");
	#elif defined(FMS_BENCH_MOTOR)
		debugln("FMS_BENCH_V5 MOTOR_GATED_CH8 LOW_THROTTLE_REQUIRED");
	#else
		debugln("FMS_BENCH_V4 RUD_REVERSE CH5_MODE CH7_BUTTON T_LOCK=1989");
	#endif
	#ifdef FMS_CONTINUOUS
		debugln("SA controls RF. SD controls motor. NO_AUTO_TIMEOUT. GPS_FAILSAFE_UNTESTED.");
	#else
		debugln("Arm requires option42 + CH16high after observed disarm. Limit30s.");
	#endif
}

static uint16_t FMS_Bench_callback()
{
	#ifdef FMS_BENCH_INPUT_ONLY
		if((uint32_t)(millis()-fms_bench_stats)>=500UL)
		{
			fms_bench_stats=millis();
			debugln("BENCH_INPUT OPT=%d CH16=%u",option,Channel_data[CH16]);
			debug("INPUT_CH1_8=");
			for(uint8_t i=0;i<8;i++) debug(" %u",Channel_data[i]);
			debugln("");
			debug("INPUT_CH9_16=");
			for(uint8_t i=8;i<16;i++) debug(" %u",Channel_data[i]);
			debugln("");
		}
		return 1000; // Compile-time diagnostic gate BEFORE every TX/arming path.
	#endif
	uint32_t now=millis();
	if(!IS_INPUT_SIGNAL_on || (uint32_t)(now-fms_bench_last_callback)>100)
	{
		FMS_Bench_stop();
		fms_bench_seen_disarm=false; // No automatic RF resume after missing input.
	}
	fms_bench_last_callback=now;
	bool requested=FMS_bench_request(option,Channel_data[CH16],sub_protocol,RX_num);
	if(!requested)
	{
		if(fms_bench_active) { FMS_Bench_stop(); debugln("BENCH_DISARMED"); }
		if((uint32_t)(now-fms_bench_stats)>=500UL)
		{
			fms_bench_stats=now;
			#ifdef FMS_BENCH_MOTOR
				debugln("BENCH_IDLE O=%d SA=%u SD=%u THR=%u SE=%u SC=%u INHIBITED",option,Channel_data[CH16],Channel_data[CH8],Channel_data[THROTTLE],Channel_data[CH7],Channel_data[CH5]);
			#else
				debugln("BENCH_IDLE OPT=%d CH16=%u CH7=%u CH5=%u RF_INHIBITED",option,Channel_data[CH16],Channel_data[CH7],Channel_data[CH5]);
			#endif
		}
		#ifdef FMS_RELEASE
			// Changing an invalid menu/profile to valid with SA already high
			// must never substitute for a physical SA OFF -> ON sequence.
			fms_bench_seen_disarm=Channel_data[CH16]<=1800;
		#else
			fms_bench_seen_disarm=true;
		#endif
		return 1000;
	}
	if(!fms_bench_active)
	{
		if(!fms_bench_seen_disarm) return 1000;
		fms_bench_seen_disarm=false;
		static_assert(sizeof(hopping_frequency)>=41,"Need at least41 hopping entries");
		const uint8_t address[5]={0x7F,0xFF,0xFF,0xFF,0x7F};
		XN297_Configure(XN297_CRCEN,XN297_SCRAMBLED,XN297_250K);
		#ifdef FMS_RELEASE
			option_override=1; // XN297_Configure otherwise advertises RF fine tune.
		#endif
		XN297_SetTXAddr(address,5);
		for(uint8_t i=0;i<41;i++) hopping_frequency[i]=fms_bench_hops[i];
		CC2500_250K_HoppingCalib(41);
		CC2500_WriteReg(CC2500_0C_FSCTRL0,0);
		XN297_SetTxRxMode(TX_EN);
		// Lowest predefined range-test chip setting, not measured radiated power.
		CC2500_WriteReg(CC2500_3E_PATABLE,CC2500_RANGE_POWER);
		fms_bench_index=0;
		fms_bench_rolling=0;
		fms_bench_started=millis();
		fms_bench_stats=fms_bench_started;
		fms_bench_active=true;
		#if defined(FMS_CONTINUOUS)
			debugln("CONTROL_ARMED MOTOR_SEPARATELY_GATED NO_AUTO_TIMEOUT");
		#elif defined(FMS_BENCH_MOTOR)
			debugln("BENCH_ARMED MOTOR_SEPARATELY_GATED LIMIT_MS=30000");
		#else
			debugln("BENCH_ARMED THROTTLE_LOCK=1989 LIMIT_MS=30000");
		#endif
	}
	#ifndef FMS_CONTINUOUS
	if((uint32_t)(millis()-fms_bench_started)>=30000UL)
	{
		FMS_Bench_stop();
		debugln("BENCH_TIMEOUT: disarm before retry");
		return 1000;
	}
	#endif
	uint8_t outgoing[16];
	uint16_t throttle_value=1989;
	#ifdef FMS_BENCH_MOTOR
		bool motor_enabled=FMS_motor_step(fms_motor_gate,true,Channel_data[CH8],Channel_data[THROTTLE]);
		throttle_value=FMS_motor_value(Channel_data[THROTTLE],motor_enabled);
	#endif
	FMS_bench_pack(outgoing,Channel_data[AILERON],Channel_data[ELEVATOR],Channel_data[RUDDER],fms_bench_rolling,Channel_data[CH7],Channel_data[CH5],throttle_value);
	CC2500_Strobe(CC2500_SIDLE);
	CC2500_250K_Hopping(fms_bench_index);
	XN297_WritePayload(outgoing,16);
	fms_bench_index=(fms_bench_index+1)%41;
	fms_bench_rolling=(fms_bench_rolling+1500)&4095;
	if((uint32_t)(millis()-fms_bench_stats)>=1000UL)
	{
		fms_bench_stats=millis();
		debugln("BENCH_TX C=%d A=%u E=%u R=%u T=%u BTN=%u",fms_bench_hops[(fms_bench_index+40)%41],FMS_bench_scale(Channel_data[AILERON]),FMS_bench_scale(Channel_data[ELEVATOR]),3000-FMS_bench_scale(Channel_data[RUDDER]),throttle_value,Channel_data[CH7]>1800?2000:1500);
		#ifdef FMS_BENCH_MOTOR
			debugln("MOTOR_GATE ENABLE=%d CH8=%u THR_RAW=%u",motor_enabled,Channel_data[CH8],Channel_data[THROTTLE]);
		#endif
	}
	return 9000;
}
#endif
