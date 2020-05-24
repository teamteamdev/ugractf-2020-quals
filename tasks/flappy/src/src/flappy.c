#include <x86intrin.h>
#include <unistd.h>
#include <cpuid.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>
#include <dpmi.h>
#include <sys/farptr.h>
#include <go32.h>

static void enter_video_mode()
{
  __dpmi_regs regs = {0};
  regs.x.ax = 0x13; /*  mode number */
  __dpmi_int(0x10, &regs);
}

static void exit_video_mode()
{
  __dpmi_regs regs = {0};
  regs.x.ax = 0x03; /*  mode number */
  __dpmi_int(0x10, &regs);
}

inline static void draw_pixel(uint16_t x, uint16_t y, uint8_t color)
{
  _farnspokeb(0xa0000 + 320 * y + x, color);
}

inline static void barrier()
{
  unsigned a = 0x1, b, c ,d;
  asm volatile ("cpuid": "=a" (a), "=b" (b), "=c" (c), "=d" (d) : "0" (a));
}

inline static void sleep_n_instructions(int n)
{
  for (int i = n; i > 0; i--) {
    barrier();
  }
}

static uclock_t zero_clock;

static void measure_zero_clock()
{
  uclock();
  barrier();
  uclock_t t_start = uclock();
  barrier();
  uclock_t t_end = uclock();
  zero_clock = t_end - t_start;
}

static float measure_clock_rate()
{
  uclock_t t_start = uclock();
  sleep_n_instructions(1000);
  uclock_t t_end = uclock();
  return (double)UCLOCKS_PER_SEC / (t_end - t_start - zero_clock);
}

static const float low_speed = 600;
static const float high_speed = 4000;

static uint16_t get_bird_elevation()
{
  float rate = measure_clock_rate();
  if (rate > 1.5 * high_speed) {
    exit_video_mode();
    printf("Wow your CPU is too fast for this game sorry.\n");
    return 1;
  }

  float pos = (rate - low_speed) / (high_speed - low_speed);
  if (pos < 0) {
    return 0;
  } else if (pos >= 1) {
    return 199;
  } else {
    // Not 200, just to be safe.
    return pos * 199;
  }
}

struct wall {
  uint16_t x;
  uint16_t elev1;
  uint16_t elev2;
};

static const struct wall walls[] = {
  { .x = 80, .elev1 = 0, .elev2 = 130 },
  { .x = 200, .elev1 = 60, .elev2 = 199 },
};

static void draw_wall(const struct wall* wall, uint16_t color)
{
  for(uint16_t y = 199 - wall->elev2; y < 199 - wall->elev1; y++) {
    draw_pixel(wall->x, y, color);
  }
}

char* show_credits();

int main()
{
  measure_zero_clock();
  enter_video_mode();
  _farsetsel(_dos_ds);

  for (size_t i = 0; i < sizeof(walls) / sizeof(walls[0]); i++)
    draw_wall(&walls[i], 4);

  for(uint16_t bird_x = 0; bird_x < 320; bird_x++) {
    uint16_t bird_elevation = get_bird_elevation();
    for (size_t i = 0; i < sizeof(walls) / sizeof(walls[0]); i++) {
      const struct wall* w = &walls[i];
      if (w->x == bird_x && bird_elevation >= w->elev1 && bird_elevation <= w->elev2) {
        exit_video_mode();
        printf("YOU LOST, you got 0 points\n");
        return 0;
      }
    }
    draw_pixel(bird_x, 199 - bird_elevation, 10);
    usleep(56 * 1000);
  }

  exit_video_mode();
  const char* credits = show_credits();
  printf("YOU WON, you got %s points\n", credits);
  return 0;
}
