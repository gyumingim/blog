---
id: 17
title: "임베디드 OS 프로젝트 Ch.5"
subtitle: "UART"
date: "2025.03.26"
thumbnail: "EmbeddedOS1.png"
---
#
## 시작하기 전
#
전 시간에서는 레지스터 값을 어떻게 바꾸는 지 알아보았습니다.
이번 시간에는 UART 통신으로 출력과 입력을 배워 볼 예정입니다
(코드 양 많음)
#
## 5.1 UART (from GPT)
#
**UART(범용 비동기 송수신기)**는 두 장치 간에 클럭 신호 없이 비동기적으로 데이터를 직렬로 전송하는 기술이다. 시작 비트와 정지 비트를 사용해 데이터 프레임을 구분하며, 오류 검출을 위한 패리티 비트를 사용할 수 있다. 주로 마이크로컨트롤러와 컴퓨터 간의 통신에 많이 사용된다.
#
UART는 주로 콘솔 입출력용으로 사용된다. 
UART를 사용할 때 UART 하드웨어의 레지스터를 코드로 가지고 있으면 바로 UART를 사용할 수 있다. 
#
오프셋이 0x00인 UARTDR은 UART Data Register의 약자
**0 ~ 7번 비트까지 입출력을 담당합니다.** 한번에 1byte를 통신할 수 있다
**8 ~ 11번 비트까지는 종류별로 정의된 에러이다.** 프레임에러, 패리티 에러, 브레이크 에러, 오버런 에러 등 이름이 붙어있다. 설명에 부합하는 에러가 발생하면 해당 비트 값이 1이 된다. 
#
___
#
> 5-2 그림
![](https://velog.velcdn.com/images/wbhaao/post/651a4241-402c-4139-87b9-5f365eec0afe/image.png){:width="500"}
#
5-2 그림을 코드로 옮기는 방법은 
1. C언어 매크로를 통해 정의를 하거나, 
2. 구조체를 이용하는 방법이 있다.` 
우리는 구조체를 이용할 것이다. 
#
_구조체 사용 코드 예시_
```c
/*
 * Uart.h
 *
 *  Created on: Sep 8, 2018
 *      Author: maanu
 */
#ifndef HAL_RVPB_UART_H_
#define HAL_RVPB_UART_H_
typedef union UARTDR_t
{
    uint32_t all;
    struct {
        uint32_t DATA:8;    // 7:0
        uint32_t FE:1;      // 8
        uint32_t PE:1;      // 9
        uint32_t BE:1;      // 10
        uint32_t OE:1;      // 11
        uint32_t reserved:20;
    } bits;
} UARTDR_t;
typedef union UARTRSR_t
{
    uint32_t all;
    struct {
        uint32_t FE:1;      // 0
        uint32_t PE:1;      // 1
        uint32_t BE:1;      // 2
        uint32_t OE:1;      // 3
        uint32_t reserved:28;
    } bits;
} UARTRSR_t;
typedef union UARTFR_t
{
    uint32_t all;
    struct {
        uint32_t CTS:1;     // 0
        uint32_t DSR:1;     // 1
        uint32_t DCD:1;     // 2
        uint32_t BUSY:1;    // 3
        uint32_t RXFE:1;    // 4
        uint32_t TXFF:1;    // 5
        uint32_t RXFF:1;    // 6
        uint32_t TXFE:1;    // 7
        uint32_t RI:1;      // 8
        uint32_t reserved:23;
    } bits;
} UARTFR_t;
typedef union UARTILPR_t
{
    uint32_t all;
    struct {
        uint32_t ILPDVSR:8; // 7:0
        uint32_t reserved:24;
    } bits;
} UARTILPR_t;
typedef union UARTIBRD_t
{
    uint32_t all;
    struct {
        uint32_t BAUDDIVINT:16; // 15:0
        uint32_t reserved:16;
    } bits;
} UARTIBRD_t;
typedef union UARTFBRD_t
{
    uint32_t all;
    struct {
        uint32_t BAUDDIVFRAC:6; // 5:0
        uint32_t reserved:26;
    } bits;
} UARTFBRD_t;
typedef union UARTLCR_H_t
{
    uint32_t all;
    struct {
        uint32_t BRK:1;     // 0
        uint32_t PEN:1;     // 1
        uint32_t EPS:1;     // 2
        uint32_t STP2:1;    // 3
        uint32_t FEN:1;     // 4
        uint32_t WLEN:2;    // 6:5
        uint32_t SPS:1;     // 7
        uint32_t reserved:24;
    } bits;
} UARTLCR_H_t;
typedef union UARTCR_t
{
    uint32_t all;
    struct {
        uint32_t UARTEN:1;      // 0
        uint32_t SIREN:1;       // 1
        uint32_t SIRLP:1;       // 2
        uint32_t Reserved1:4;   // 6:3
        uint32_t LBE:1;         // 7
        uint32_t TXE:1;         // 8
        uint32_t RXE:1;         // 9
        uint32_t DTR:1;         // 10
        uint32_t RTS:1;         // 11
        uint32_t Out1:1;        // 12
        uint32_t Out2:1;        // 13
        uint32_t RTSEn:1;       // 14
        uint32_t CTSEn:1;       // 15
        uint32_t reserved2:16;
    } bits;
} UARTCR_t;
typedef union UARTIFLS_t
{
    uint32_t all;
    struct {
        uint32_t TXIFLSEL:3;    // 2:0
        uint32_t RXIFLSEL:3;    // 5:3
        uint32_t reserved:26;
    } bits;
} UARTIFLS_t;
typedef union UARTIMSC_t
{
    uint32_t all;
    struct {
        uint32_t RIMIM:1;   // 0
        uint32_t CTSMIM:1;  // 1
        uint32_t DCDMIM:1;  // 2
        uint32_t DSRMIM:1;  // 3
        uint32_t RXIM:1;    // 4
        uint32_t TXIM:1;    // 5
        uint32_t RTIM:1;    // 6
        uint32_t FEIM:1;    // 7
        uint32_t PEIM:1;    // 8
        uint32_t BEIM:1;    // 9
        uint32_t OEIM:1;    // 10
        uint32_t reserved:21;
    } bits;
} UARTIMSC_t;
typedef union UARTRIS_t
{
    uint32_t all;
    struct {
        uint32_t RIRMIS:1;  // 0
        uint32_t CTSRMIS:1; // 1
        uint32_t DCDRMIS:1; // 2
        uint32_t DSRRMIS:1; // 3
        uint32_t RXRIS:1;   // 4
        uint32_t TXRIS:1;   // 5
        uint32_t RTRIS:1;   // 6
        uint32_t FERIS:1;   // 7
        uint32_t PERIS:1;   // 8
        uint32_t BERIS:1;   // 9
        uint32_t OERIS:1;   // 10
        uint32_t reserved:21;
    } bits;
} UARTRIS_t;
typedef union UARTMIS_t
{
    uint32_t all;
    struct {
        uint32_t RIMMIS:1;  // 0
        uint32_t CTSMMIS:1; // 1
        uint32_t DCDMMIS:1; // 2
        uint32_t DSRMMIS:1; // 3
        uint32_t RXMIS:1;   // 4
        uint32_t TXMIS:1;   // 5
        uint32_t RTMIS:1;   // 6
        uint32_t FEMIS:1;   // 7
        uint32_t PEMIS:1;   // 8
        uint32_t BEMIS:1;   // 9
        uint32_t OEMIS:1;   // 10
        uint32_t reserved:21;
    } bits;
} UARTMIS_t;
typedef union UARTICR_t
{
    uint32_t all;
    struct {
        uint32_t RIMIC:1;   // 0
        uint32_t CTSMIC:1;  // 1
        uint32_t DCDMIC:1;  // 2
        uint32_t DSRMIC:1;  // 3
        uint32_t RXIC:1;    // 4
        uint32_t TXIC:1;    // 5
        uint32_t RTIC:1;    // 6
        uint32_t FEIC:1;    // 7
        uint32_t PEIC:1;    // 8
        uint32_t BEIC:1;    // 9
        uint32_t OEIC:1;    // 10
        uint32_t reserved:21;
    } bits;
} UARTICR_t;
typedef union UARTDMACR_t
{
    uint32_t all;
    struct {
        uint32_t RXDMAE:1;  // 0
        uint32_t TXDMAE:1;  // 1
        uint32_t DMAONERR:1;// 2
        uint32_t reserved:29;
    } bits;
} UARTDMACR_t;
typedef struct PL011_t
{
    UARTDR_t    uartdr;         //0x000
    UARTRSR_t   uartrsr;        //0x004
    uint32_t    reserved0[4];   //0x008-0x014
    UARTFR_t    uartfr;         //0x018
    uint32_t    reserved1;      //0x01C
    UARTILPR_t  uartilpr;       //0x020
    UARTIBRD_t  uartibrd;       //0x024
    UARTFBRD_t  uartfbrd;       //0x028
    UARTLCR_H_t uartlcr_h;      //0x02C
    UARTCR_t    uartcr;         //0x030
    UARTIFLS_t  uartifls;       //0x034
    UARTIMSC_t  uartimsc;       //0x038
    UARTRIS_t   uartris;        //0x03C
    UARTMIS_t   uartmis;        //0x040
    UARTICR_t   uarticr;        //0x044
    UARTDMACR_t uartdmacr;      //0x048
} PL011_t;
#define UART_BASE_ADDRESS0       0x10009000
#define UART_INTERRUPT0          44
#endif /* HAL_RVPB_UART_H_ */
```
#
UART 하드웨어를 제어 할 수 있는 변수를 선언하기 위해서 Regs.c 파일을 생성
#
_Regs.c_
```c
/*
 * Regs.c
 *
 *  Created on: Sep 8, 2018
 *      Author: maanu
 */
#include "stdint.h"
#include "Uart.h"
volatile PL011_t* Uart = (PL011_t*)UART_BASE_ADDRESS0;
```
#
## PLUS HAL
#
HAL(Hardware Abstraction Layer)은 운영 체제와 하드웨어 간의 중재 역할을 하는 소프트웨어 계층으로, 다양한 하드웨어를 추상화하여 일관된 인터페이스를 제공한다. 이를 통해 개발자는 하드웨어의 세부 사항에 구애받지 않고 응용 프로그램을 개발할 수 있으며, 시스템의 이식성과 호환성을 높일 수 있다. HAL은 특히 드라이버 개발과 시스템 안정성 유지에 중요한 역할을 한다.
#
_현재 파일구조_
```
--boot
|  |--Entry.S
|  |--Main.c
|
--hal
|  |--HalUart.h
|  |--rvpb
|  	   |--Uart.h
|
--include
|     |--ARMv7AR.h
|     |--MemoryMap.h
|     |--stdint.h
|
--Makefile
--navilos
--README.md
```
#
HARUART.h 파일을 생성합니다. 
#
_HALUART.h 코드_
```c
/*
 * HalUart.h
 *
 *  Created on: Sep 8, 2018
 *      Author: maanu
 */
#ifndef HAL_HALUART_H_
#define HAL_HALUART_H_
void    Hal_uart_init(void);
void    Hal_uart_put_char(uint8_t ch);
#endif /* HAL_HALUART_H_ */
```
#
UART 공용 API를 설계했습니다. 
해당 API를 만족하는 코드를 만들기 위해 Uart.c 파일을 재구성해야합니다.
#
_Uart.c 코드_
```c
/*
 * Uart.c
 *
 *  Created on: Sep 8, 2018
 *      Author: maanu
 */
#include "stdint.h"  // 표준 정수 타입 정의를 포함하는 헤더 파일
#include "Uart.h"    // UART 관련 헤더 파일
#include "HalUart.h" // HAL (Hardware Abstraction Layer) UART 관련 헤더 파일
// 외부에서 선언된 volatile 타입의 PL011_t 구조체 포인터 변수 Uart
extern volatile PL011_t* Uart;
/*
 * Hal_uart_init
 * UART를 초기화하는 함수
 */
void Hal_uart_init(void)
{
    // UART를 비활성화
    Uart->uartcr.bits.UARTEN = 0;
    // 송신(TX)을 활성화
    Uart->uartcr.bits.TXE = 1;
    // 수신(RX)을 활성화
    Uart->uartcr.bits.RXE = 1;
    // UART를 활성화
    Uart->uartcr.bits.UARTEN = 1;
}
```
#
코드가 정상적으로 작동된다면 실행되는 순간 UART를 통해서데이터가 호스트로 전송됩니다. 
#
_Main.c 코드_
```c
#include "stdint.h"  // 표준 정수 타입 정의를 포함하는 헤더 파일
#include "HalUart.h" // HAL (Hardware Abstraction Layer) UART 관련 헤더 파일
#include "stdio.h"   // 표준 입출력 함수들을 포함하는 헤더 파일
static void Hw_init(void);     // 하드웨어 초기화 함수의 정적 선언
void main(void)  // 메인 함수의 정의
{
    Hw_init(); // 하드웨어 초기화 함수 호출
    uint32_t i = 100; // 카운터 변수 초기화
    while(i--)  // 카운터가 0이 될 때까지 반복
    {
        Hal_uart_put_char('N'); // UART로 문자 'N'을 전송
    }
}
static void Hw_init(void)  // 하드웨어 초기화 함수의 정의
{
    Hal_uart_init(); // UART 초기화 함수 호출
}
```
#
makefile을 구성 한 다음에 결과를 확인해봅시다.
#
_Makefile_
```bash
ARCH = armv7-a  # 아키텍처 설정
MCPU = cortex-a8  # CPU 설정
CC = arm-none-eabi-gcc  # C 컴파일러 설정
AS = arm-none-eabi-as  # 어셈블러 설정
LD = arm-none-eabi-ld  # 링커 설정
OC = arm-none-eabi-objcopy  # 오브젝트 복사기 설정
LINKER_SCRIPT = ./navilos.ld  # 링커 스크립트 파일 경로
MAP_FILE = build/navilos.map  # 맵 파일 경로
ASM_SRCS = $(wildcard boot/*.S)  # 어셈블리 소스 파일 목록
ASM_OBJS = $(patsubst boot/%.S, build/%.os, $(ASM_SRCS))  # 어셈블리 오브젝트 파일 목록
C_SRCS = $(wildcard boot/*.c)  # C 소스 파일 목록
C_OBJS = $(patsubst boot/%.c, build/%.o, $(C_SRCS))  # C 오브젝트 파일 목록
INC_DIRS  = -I include  # 포함 디렉토리 설정
navilos = build/navilos.axf  # 생성될 실행 파일 경로
navilos_bin = build/navilos.bin  # 생성될 바이너리 파일 경로
.PHONY: all clean run debug gdb  # 가상 타겟 설정
all: $(navilos)  # 기본 타겟 설정
clean:  # 빌드 디렉토리 정리 타겟
	@rm -fr build
run: $(navilos)  # 실행 타겟
	qemu-system-arm -M realview-pb-a8 -kernel $(navilos)
debug: $(navilos)  # 디버그 타겟
	qemu-system-arm -M realview-pb-a8 -kernel $(navilos) -S -gdb tcp::1234,ipv4
gdb:  # GDB 실행 타겟
	arm-none-eabi-gdb
$(navilos): $(ASM_OBJS) $(C_OBJS) $(LINKER_SCRIPT)  # 실행 파일 생성 타겟
	$(LD) -n -T $(LINKER_SCRIPT) -o $(navilos) $(ASM_OBJS) $(C_OBJS) -Map=$(MAP_FILE)
	$(OC) -O binary $(navilos) $(navilos_bin)
build/%.os: $(ASM_SRCS)  # 어셈블리 오브젝트 파일 생성 타겟
	mkdir -p $(shell dirname $@)
	$(CC) -march=$(ARCH) -mcpu=$(MCPU) $(INC_DIRS) -c -g -o $@ $<
build/%.o: $(C_SRCS)  # C 오브젝트 파일 생성 타겟
	mkdir -p $(shell dirname $@)
	$(CC) -march=$(ARCH) -mcpu=$(MCPU) $(INC_DIRS) -c -g -o $@ $<
```
#
`make run`
#
![](https://velog.velcdn.com/images/wbhaao/post/6c09599c-8790-4ee5-a729-4be2872f3e84/image.png){:width="500"}
#
N이 100번 출력되는 것을 볼 수 있다. 
#
하지만 리눅스 터미널의 입력이 QEMU와연결되어 있어 Ctrl + C로 종료할 수 없다. 
별개의 터미널로 kill 명령어를 통해 QEMU 를 종료 시킬 수 있다. 
#
## 5.2 안녕 세상!
#
평소 코딩을 시작할 때 가장 먼저 보여주는 예제는 `printf("Hello world");` 입니다. python, C를 배울때는 그냥 써도 됐었지만, 
펌웨어에서는 `printf()`를 직접 만들어야한다. 
#
그러므로 stdio.h, stdio.c 파일을 만들 것이다. 
#
_stdio.h_
```c
/*
 * stdio.h
 *
 *  Created on: Sep 17, 2018
 *      Author: maanu
 */
#ifndef LIB_STDIO_H_
#define LIB_STDIO_H_
uint32_t putstr(const char* s);
#endif /* LIB_STDIO_H_ */
```
#
_stdio.c_
```c
/*
 * stdio.c
 *
 *  Created on: Sep 17, 2018
 *      Author: maanu
 */
#include "stdint.h"
#include "HalUart.h"
#include "stdio.h"
uint32_t putstr(const char* s)
{
    uint32_t c = 0;
    while(*s)
    {
        Hal_uart_put_char(*s++);
        c++;
    }
    return c;
}
```
#
이제 hello world를 출력할 수 있도록 main.c 파일에 putchr 함수를 넣어줍시다. 
#
_Main.c_
```c
#include "stdint.h"
#include "HalUart.h"
#include "stdio.h"
static void Hw_init(void);
void main(void)
{
    Hw_init();
    uint32_t i = 100;
    while(i--)
    {
        Hal_uart_put_char('N');
    }
    Hal_uart_put_char('\n');
    putstr("Hello World!\n");
}
static void Hw_init(void)
{
    Hal_uart_init();
}
```
#
`make run`
#
![](https://velog.velcdn.com/images/wbhaao/post/b277c7d9-4e51-4cb4-acbe-a0edbaecdffc/image.png){:width="500"}
#
Hello World! 가 잘  출력되는 것을 볼 수 있다. 
#
## 5.3 UART로 입력받기
#
이제 UART로 출력을 해보았으니 입력 또한 구현해보겠습니다. 
우리가 **출력**을 할 때에는 
#
1. 보내기 버퍼가 비었는지, 비어있으면 
2. 데이터 레지스터를 통해 데이터를 보내기 버퍼로 보내고, 
3. 하드웨어가 알아서 나머지 작업을 처리해주고 
4. 하드웨어와 연결된 콘솔에 데이터가 나타납니다. 
#
**입력**은 그와 반대로 
#
1. 받기 버퍼가 채워져있는지 확인하고, 채워져 있다면 
2. 데이터 레지스터를 통해 데이터를 읽어오면 됩니다. 
#
입력받는 함수는 코드 구성에 따라 성능이 크게 달라지게 됩니다. 
저는 바로 최적화 코드로 구성하겠습니다.
#
_Hal_uart_get_char() - [Uart.c]_
```c
uint8_t Hal_uart_get_char(void)
{
    uint32_t data;
    while(Uart->uartfr.bits.RXFE);
    data = Uart->uartdr.all;
    // Check for an error flag
    if (data & 0xFFFFFF00)
    {
        // Clear the error
        Uart->uartrsr.all = 0xFF;
        return 0;
    }
    return (uint8_t)(data & 0xFF);
}
```
#
![](https://velog.velcdn.com/images/wbhaao/post/c52da9d9-04f7-4909-bd15-ffa6cf317266/image.png){:width="500"}
#
최적화가 되지 않은 코드는 약 340바이트가 생성되지만 
이 코드는 총 200바이트짜리 바이너리가 생성됩니다. 
#
만든 함수를 Main.c에 넣어봅시다
#
_Main.c_
```c
#include "stdint.h"
#include "HalUart.h"
#include "stdio.h"
static void Hw_init(void);
void main(void)
{
    Hw_init();
    uint32_t i = 100;
    while(i--)
    {
        Hal_uart_put_char('N');
    }
    Hal_uart_put_char('\n');
    putstr("Hello World!\n");
    i = 100;
    while(i--)
    {
        uint8_t ch = Hal_uart_get_char();
        Hal_uart_put_char(ch);
    }
}
static void Hw_init(void)
{
    Hal_uart_init();
}
```
#
![](https://velog.velcdn.com/images/wbhaao/post/18c15a29-8828-467b-a4ae-435cbc63292e/image.png)
#
잘 입력되는 걸 확인 할 수 있습니다. 
#
## 5.4 printf 만들기
#
우리가 쓰던 `printf`와 실제 `printf`의 차이점은 포맷을 쓸 수 있나, 없나 입니다. 포맷은 `%s, %d` 같이 데이터를 출력하는 형식을 지정할 수 있다는 것입니다. 다른 기능들이 많지만 우리는 필요한 기능만 만들어 볼 것입니다. 우리는 `debug_printf()`를 만들 것 입니다. 
#
_debug_printf() 선언_
```c
uint32_t debug_printf(const char* format, ...)
{
    va_list args;
    va_start(args, format);
    vsprintf(printf_buf, format, args);
    va_end(args);
    return putstr(printf_buf);
}
```
#
코드가 생각보다 간단합니다. 다음으로 stdarg.h 코드를 작성해보겠습니다. 
#
_stdarg.h_
```c
/*
 * stdarg.h
 *
 *  Created on: Sep 19, 2018
 *      Author: maanu
 */
#ifndef INCLUDE_STDARG_H_
#define INCLUDE_STDARG_H_
typedef __builtin_va_list va_list;
#define va_start(v,l)   __builtin_va_start(v,l)
#define va_end(v)       __builtin_va_end(v)
#define va_arg(v,l)     __builtin_va_arg(v,l)
#endif /* INCLUDE_STDARG_H_ */
```
#
GCC 표준 라이브러리의 기존 stdarg.h 파일은 더 복잡합니다. 
그래서 필요한 부분만 복사해서 사용합니다. 
#
stdio.h 파일에서 include만 사용하면, va_list, va_start, va_end를 사용 할 수 있게 됩니다. 
#
_stdio.h_
```
/*
 * stdio.h
 *
 *  Created on: Sep 17, 2018
 *      Author: maanu
 */
#ifndef LIB_STDIO_H_
#define LIB_STDIO_H_
#include "stdarg.h"
typedef enum utoa_t
{
    utoa_dec = 10,
    utoa_hex = 16,
} utoa_t;
uint32_t putstr(const char* s);
uint32_t debug_printf(const char* format, ...);
uint32_t vsprintf(char* buf, const char* format, va_list arg);
uint32_t utoa(char* buf, uint32_t val, utoa_t base);
#endif /* LIB_STDIO_H_ */
```
#
stdio.h에 stdarg.h파일을 불러옵니다
#
_vsprintf() 함수_
```c
uint32_t vsprintf(char* buf, const char* format, va_list arg)
{
    uint32_t c = 0;
    char     ch;
    char*    str;
    uint32_t uint;
    uint32_t hex;
    for (uint32_t i = 0 ; format[i] ; i++)
    {
        if (format[i] == '%')
        {
            i++;
            switch(format[i])
            {
            case 'c':
                ch = (char)va_arg(arg, int32_t);
                buf[c++] = ch;
                break;
            case 's':
                str = (char*)va_arg(arg, char*);
                if (str == NULL)
                {
                    str = "(null)";
                }
                while(*str)
                {
                    buf[c++] = (*str++);
                }
                break;
            case 'u':
                uint = (uint32_t)va_arg(arg, uint32_t);
                c += utoa(&buf[c], uint, utoa_dec);
                break;
            case 'x':
                hex = (uint32_t)va_arg(arg, uint32_t);
                c += utoa(&buf[c], hex, utoa_hex);
                break;
            }
        }
        else
        {
            buf[c++] = format[i];
        }
    }
    if (c >= PRINTF_BUF_LEN)
    {
        buf[0] = '\0';
        return 0;
    }
    buf[c] = '\0';
    return c;
}
```
#
최소한의 기능만 구현한 vsprintf() 코드입니다.
#
_stdio.h_
```c
/*
 * stdio.h
 *
 *  Created on: Sep 17, 2018
 *      Author: maanu
 */
#ifndef LIB_STDIO_H_
#define LIB_STDIO_H_
#include "stdarg.h"
typedef enum utoa_t
{
    utoa_dec = 10,
    utoa_hex = 16,
} utoa_t;
uint32_t putstr(const char* s);
uint32_t debug_printf(const char* format, ...);
uint32_t vsprintf(char* buf, const char* format, va_list arg);
uint32_t utoa(char* buf, uint32_t val, utoa_t base);
#endif /* LIB_STDIO_H_ */
```

utoa 함수를 선언합니다. 

>stdio.c
```c
uint32_t utoa(char* buf, uint32_t val, utoa_t base)
{
    const char asciibase = 'a';
    uint32_t c = 0;
    int32_t idx = 0;
    char     tmp[11];   // It is enough for 32 bit int
    do {
        uint32_t t = val % (uint32_t)base;
        if (t >= 10)
        {
            t += asciibase - '0' - 10;
        }
        tmp[idx] = (t + '0');
        val /= base;
        idx++;
    } while(val);
    // reverse
    idx--;
    while (idx >= 0)
    {
        buf[c++] = tmp[idx];
        idx--;
    }
    return c;
}
```
#
utoa 함수를 구현합니다. 

main.c에 printf()함수를 추가하겠습니다

_Main.c_
```c
#include "stdint.h"
#include "HalUart.h"
#include "stdio.h"
static void Hw_init(void);
static void Printf_test(void);
void main(void)
{
    Hw_init();
    uint32_t i = 100;
    while(i--)
    {
        Hal_uart_put_char('N');
    }
    Hal_uart_put_char('\n');
    putstr("Hello World!\n");
    Printf_test();
    i = 100;
    while(i--)
    {
        uint8_t ch = Hal_uart_get_char();
        Hal_uart_put_char(ch);
    }
}
static void Hw_init(void)
{
    Hal_uart_init();
}
static void Printf_test(void)
{
    char* str = "printf pointer test";
    char* nullptr = 0;
    uint32_t i = 5;
    debug_printf("%s\n", "Hello printf");
    debug_printf("output string pointer: %s\n", str);
    debug_printf("%s is null pointer, %u number\n", nullptr, 10);
    debug_printf("%u = 5\n", i);
    debug_printf("dec=%u hex=%x\n", 0xff, 0xff);
}
```
#
이후 make run을 동작시키면 에러가 뜰 것입니다.
왜냐면 utoa()에서는 나머지, 나누기 연산이 쓰이지만 ARM은 기본적으로 나머지, 나누기 연산을 지원하는 하드웨어가 없다고 간주합니다. 그러므로 GCC가 이를 소프트웨어로 구현해놓은 라이브러리 함수로 자동으로 링킹해야 합니다. 
#
즉 makefile을 조금 수정하겠습니다. 
#
_Makefile_
```bash
ARCH = armv7-a
MCPU = cortex-a8
TARGET = rvpb
CC = arm-none-eabi-gcc
AS = arm-none-eabi-as
LD = arm-none-eabi-gcc
OC = arm-none-eabi-objcopy
LINKER_SCRIPT = ./navilos.ld
MAP_FILE = build/navilos.map
ASM_SRCS = $(wildcard boot/*.S)
ASM_OBJS = $(patsubst boot/%.S, build/%.os, $(ASM_SRCS))
VPATH = boot 			\
        hal/$(TARGET)	\
        lib
C_SRCS  = $(notdir $(wildcard boot/*.c))
C_SRCS += $(notdir $(wildcard hal/$(TARGET)/*.c))
C_SRCS += $(notdir $(wildcard lib/*.c))
C_OBJS = $(patsubst %.c, build/%.o, $(C_SRCS))
INC_DIRS  = -I include 			\
            -I hal	   			\
            -I hal/$(TARGET)	\
            -I lib
CFLAGS = -c -g -std=c11 -mthumb-interwork
LDFLAGS = -nostartfiles -nostdlib -nodefaultlibs -static -lgcc
navilos = build/navilos.axf
navilos_bin = build/navilos.bin
.PHONY: all clean run debug gdb
all: $(navilos)
clean:
	@rm -fr build
run: $(navilos)
	qemu-system-arm -M realview-pb-a8 -kernel $(navilos) -nographic
debug: $(navilos)
	qemu-system-arm -M realview-pb-a8 -kernel $(navilos) -S -gdb tcp::1234,ipv4
gdb:
	arm-none-eabi-gdb
kill:
	kill -9 `ps aux | grep 'qemu' | awk 'NR==1{print $$2}'`
$(navilos): $(ASM_OBJS) $(C_OBJS) $(LINKER_SCRIPT)
	$(LD) -n -T $(LINKER_SCRIPT) -o $(navilos) $(ASM_OBJS) $(C_OBJS) -Wl,-Map=$(MAP_FILE) $(LDFLAGS)
	$(OC) -O binary $(navilos) $(navilos_bin)
build/%.os: %.S
	mkdir -p $(shell dirname $@)
	$(CC) -march=$(ARCH) -mcpu=$(MCPU) -marm $(INC_DIRS) $(CFLAGS) -o $@ $<
build/%.o: %.c
	mkdir -p $(shell dirname $@)
	$(CC) -march=$(ARCH) -mcpu=$(MCPU) -marm $(INC_DIRS) $(CFLAGS) -o $@ $<
```
#
`make run`
#
![](https://velog.velcdn.com/images/wbhaao/post/3967563b-dcbe-4491-b4b0-d74c61a32e3f/image.png){:height="500"}
#
굳굳
#
_지금까지 파일구조 입니다_
```
.
├── ARMv7AR.h
├── Makefile
├── MemoryMap.h
├── boot
│   ├── Entry.S
│   ├── Entry.bin
│   ├── Entry.o
│   └── Main.c
├── build
│   ├── Entry.os
│   ├── Main.o
│   ├── Regs.o
│   ├── Uart.o
│   ├── navilos.axf
│   ├── navilos.bin
│   ├── navilos.map
│   └── stdio.o
├── em.em
├── hal
│   ├── HalUart.h
│   └── rvpb
│       ├── Regs.c
│       ├── Uart.c
│       ├── Uart.h
│       └── Uart.o
├── hello.txt
├── include
│   ├── ARMv7AR.h
│   ├── MemoryMap.h
│   ├── stdarg.h
│   └── stdint.h
├── lib
│   ├── stdio.c
│   └── stdio.h
├── navilos.axf
├── navilos.ld
└── temp
    └── SYS_ID_analysis.py

```
