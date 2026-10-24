// Local release entry; reuse the exact v6 wire encoder and safety state machine.
// Profile 5 identifies only the captured receiver/transmitter pair.
#ifdef FMSBEAVER_CC2500_INO
static void FMSBeaver_init()
{
	FMS_Bench_init();
}

static uint16_t FMSBeaver_callback()
{
	return FMS_Bench_callback();
}
#endif
