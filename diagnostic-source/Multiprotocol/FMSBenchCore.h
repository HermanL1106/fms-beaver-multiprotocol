#ifndef FMS_BENCH_CORE_H
#define FMS_BENCH_CORE_H
#include <stdint.h>

static const uint8_t fms_bench_hops[41]={2,75,26,54,4,74,40,8,73,45,6,72,30,50,10,70,34,12,36,69,38,13,68,58,14,66,18,28,52,62,20,61,29,60,22,46,24,44,56,42,76};

static uint16_t FMS_bench_scale(uint16_t raw)
{
	if(raw<204) raw=204;
	if(raw>1844) raw=1844;
	return 1000+(uint32_t)(raw-204)*1000/1640;
}

struct FMSMotorGate {
	bool seen_off=false;
	bool enabled=false;
};
static bool FMS_motor_step(FMSMotorGate& gate,bool radio_active,uint16_t motor_switch,uint16_t throttle)
{
	if(!radio_active) { gate.seen_off=false; gate.enabled=false; return false; }
	if(motor_switch<=1800) { gate.seen_off=true; gate.enabled=false; return false; }
	if(!gate.enabled && gate.seen_off)
	{
		gate.seen_off=false; // A failed high-throttle attempt requires a new OFF/ON.
		gate.enabled=throttle<=220;
	}
	return gate.enabled;
}
static uint16_t FMS_motor_value(uint16_t raw,bool enabled)
{
	if(!enabled || raw<=220) return 1989;
	return 1989-(uint32_t)(FMS_bench_scale(raw)-1000)*989/1000;
}

// Bench defaults to physical-low throttle unless an explicit gated value is supplied.
// Unknown prefix/suffix are specific to the captured transmitter, not generic IDs.
static void FMS_bench_pack(uint8_t* payload,uint16_t a,uint16_t e,uint16_t r,uint16_t rolling,uint16_t button=1024,uint16_t mode=1844,uint16_t throttle=1989)
{
	uint16_t mode_value=mode<600?1000:(mode>1400?2000:1500);
	uint16_t values[8]={FMS_bench_scale(a),FMS_bench_scale(e),throttle,(uint16_t)(3000-FMS_bench_scale(r)),mode_value,1500,(uint16_t)(button>1800?2000:1500),(uint16_t)(rolling&4095)};
	payload[0]=0x67; payload[1]=0x10;
	for(uint8_t i=0;i<8;i++) payload[2+i]=values[i]&255;
	for(uint8_t i=0;i<4;i++) payload[10+i]=(values[2*i]>>8)|((values[2*i+1]>>8)<<4);
	payload[14]=0x51; payload[15]=0x40;
}

static bool FMS_bench_request(uint8_t opt,uint16_t ch16,uint8_t sub,uint8_t rx)
{
	return opt==42 && ch16>1800 && sub==0 && rx==5;
}
#endif
