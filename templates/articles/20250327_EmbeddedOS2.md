---
id: 14
title: "[요약] 🖥️임베디드 OS 프로젝트 Ch.2"
subtitle: "일단 시작하기"
date: "2025.03.26"
thumbnail: "EmbeddedOS1.png"
---
#
<img src="../../static/image/EmbeddedOS1.png" height="200">

#
## 시작하기 전
책에서 사용하는 소스 코드들을 해당 레포지토리에서 살펴볼 수 있습니다.
#
[깃허브 레포지토리 링크](https://github.com/navilera/Navilos)
#
### 3.1 리셋 벡터
#
ARM 코어에 전원이 들어가면 리셋 벡터에 있는 명령을 먼저 실행시킵니다.
#
리셋 벡터의 메모리 주소는 0x00000000입니다.
#
Entry.S 소스 코드
#
```c
.text
	.code 32

	.global vector_start
	.global vector_end

	vector_start:
		MOV		R0, R1
	vector_end:
		.space 1024, 0
.end
```
#
>  .text 섹션을 정의한다
.code 32는 한 명령어의 크기가 32bits = 4Bytes임을 의미한다.
.global 지시어는 C의 extern과 동일하며 전역변수를 의미한다.
vector_start 레이블에서는 R1의 값을 R0로 옮기는 작업을 수행한다.
vector_end 레이블에서는 현재 위치로부터 1,024bytes를 0으로 채우는 작업을 수행한다.
#
Entry.S 파일을 컴파일하고 바이너리를 덤프해봤습니다.
#
```c
arm-none-eabi-as -march=armv7-a -mcpu=cortex-a8 -o Entry.o ./Entry.S
arm-none-eabi-objcopy -O binary Entry.o Entry.bin

hexdump Entry.bin
```
#
0001 e1a0이 보입니다.
#
예상한 대로 제대로 바이너리 파일이 생성됐습니다.
#
### 3.2 실행 파일 만들기
#
QEMU가 펌웨어 파일을 읽어서 부팅하려면 지정한 펌웨어 바이너리 파일이 ELF 파일 형식이여야 합니다.
#
arm-none-eabi-as를 이용하여 생성한 Entry.o 파일이 ELF 파일입니다.
#
ELF 파일을 만들려면 링커의 도움이 필요합니다.
#
링커가 동작하려면 링커 스크립트를 작성해야 합니다.
#
(보통 애플리케이션을 만들 때는 신경쓰지 않지만, 펌웨어를 개발할 때는 다르다고 합니다.)
#
navilos.ld 소스코드
#
```c
ENTRY(vector_start)
SECTIONS
{
	. = 0x0;


	.text :
	{
		*(vector_start)
		*(.text .rodata)
	}
	.data :
	{
		*(.data)
	}
	.bss :
	{
		*(.bss)
	}
} 
```
#
아래 명령어를 이용하여 실행 파일을 만들어줍니다.
#
```
arm-none-eabi-ld -n -T ./navilos.ld -o navilos.axf boot/Entry.o
```
#
arm-none-eabi-objdump 명령어를 사용하여 파일이 어떤 명령어로 구성되어 있는지 확인해봤습니다.
디스어셈블한 결과를 살펴보면 mov r0, r1 명령어가 잘 배치되어 있습니다.

#

![](https://velog.velcdn.com/images/wbhaao/post/48637da2-8993-4ea6-8264-aca08c2d7a02/image.png){:width="300"}

#
### 3.3 QEMU에서 실행해보기
#
실행 파일을 만들어봤지만 터미널에서 실행시키려 시도해보면 안 됩니다.

ARM 개발 보드에 다운로드 시켜서 동작을 확인하거나 QEMU로 실행해보면 됩니다.
#
```
qemu-system-arm -M realview-pb-a8 -kernel navilos.axf -S gdb tcp::1234, ipv4
```
#
실습을 하는 도중 문제가 발생했습니다.

arm-none-eabi-gdb 파일이 어디있는지 찾을 수가 없다고 합니다.
#
 ![](https://velog.velcdn.com/images/wbhaao/post/7ac5964a-3b3c-46ce-bb90-47b77e4550d2/image.png){:width="600"}
#
[askubuntu](https://askubuntu.com/questions/1031103/how-can-i-install-gdb-arm-none-eabi-on-ubuntu-18-04-bionic-beaver) 사이트에서 저랑 같은 문제를 겪은 사람들을 찾아봤고 실제로 존재했습니다.

내용을 살펴보니, gdb-multiarch 패키지를 설치하는 것을 추천하는 답변이 있었습니다.
#
```
sudo apt-get update
sudo apt-get install gdb-multiarch
```
#
잘 동작하는 것을 보아, 실습을 진행하는 데 딱히 문제는 없어보입니다.
#
```
gdb-multiarch
```
#
![](https://velog.velcdn.com/images/wbhaao/post/e5da2d05-ce85-4061-beef-7fac5705db05/image.png){:width="500"}
#
### 3.4 빌드 자동화하기
#
일단 make와 관련된 패키지들을 설치했습니다.
#
```
sudo apt-get install make
```
#
Makefile을 만들어서 빌드를 자동화해봤습니다.
#
책에서 나온 코드와 조금 달라진 점이 존재합니다.
#
```Makefile
# 타겟 아키텍처와 CPU를 지정합니다.
ARCH = armv7-a
MCPU = cortex-a8

# GNU ARM Embedded Toolchain의 도구들을 지정합니다.
CC = arm-none-eabi-gcc
AS = arm-none-eabi-as
LD = arm-none-eabi-ld
OC = arm-none-eabi-objcopy

# 링커 스크립트 파일의 경로를 지정합니다.
LINKER_SCRIPT = ./navilos.ld

# boot 디렉토리 내의 모든 어셈블리 소스 파일들을 찾습니다.
ASM_SRCS = $(wildcard boot/\*.S)

# 어셈블리 소스 파일들을 대응하는 오브젝트 파일 경로로 변환합니다.
ASM_OBJS = $(patsubst boot/%.S, build/%.o, $(ASM_SRCS))

# 최종 생성될 실행 파일과 바이너리 파일의 경로를 지정합니다.
navilos = build/navilos.axf
navilos_bin = build/navilos.bin

# 실제 파일과 관련이 없는 타겟들을 지정합니다.
.PHONY: all clean run debug gdb

# 기본 타겟으로, navilos 실행 파일을 생성합니다.
all: $(navilos)

# 빌드 과정에서 생성된 파일들을 정리합니다.
clean:
	@rm -fr build

# QEMU 에뮬레이터를 사용하여 빌드된 커널을 실행합니다.
run: $(navilos)
	qemu-system-arm -M realview-pb-a8 -kernel $(navilos)

# 디버깅 모드에서 QEMU를 사용하여 커널을 실행합니다.
# GDB 서버가 TCP 포트 1234를 통해 대기 상태가 됩니다.
debug: $(navilos)
	qemu-system-arm -M realview-pb-a8 -kernel $(navilos) -S -gdb tcp::1234,ipv4

# GNU Debugger(GDB)를 시작합니다.
gdb:
	arm-none-eabi-gdb

# navilos 실행 파일을 생성하는 규칙입니다.
# 어셈블리 오브젝트 파일들과 링커 스크립트를 사용하여 링크합니다.
# 그런 다음 objcopy를 사용하여 바이너리 파일로 변환합니다.
$(navilos): $(ASM_OBJS) $(LINKER_SCRIPT)
	$(LD) -n -T $(LINKER_SCRIPT) -o $(navilos) $(ASM_OBJS)
	$(OC) -O binary $(navilos) $(navilos_bin)

# 각 어셈블리 소스 파일을 오브젝트 파일로 컴파일하는 규칙입니다.
# 필요한 디렉토리를 생성한 후 어셈블리 파일을 컴파일합니다.
build/%.o: boot/%.S
	mkdir -p $(shell dirname $@)
	$(AS) -march=$(ARCH) -mcpu=$(MCPU) -g -o $@ $<

```
#
### 3.5 하드웨어 정보 읽어오기 - 데이터시트를 읽는 방법
#

하드웨어의 정보를 읽어오는 간단한 코드를 만들어봤습니다.
#
_Entry.S 소스 코드_
```cs
.text
	.code 32

	.global vector_start
	.global vector_end

	vector_start:
		LDR		R0, =0x10000000
		LDR		R1, [R0]
	vector_end:
		.space 1024, 0
.end
```
#
0x10000000에는 어떤 데이터가 들어있을까 궁금하여 유져 가이드 문서를 찾아봤습니다.
SYS_ID 레지스터는 0x10000000 주소에 위치하고 있으며 오로지 데이터를 읽을 수만 있답니다.
32bit 크기의 데이터를 5개의 항목으로 쪼개놓았고 각 항목이 가지는 값에 따라 의미가 존재합니다.
#
![](https://velog.velcdn.com/images/wbhaao/post/606c523f-cf27-4886-9409-fab0dc3b44de/image.png){:width="600"}
#
현재 해당 정보를 어디에 사용할 수 있을지 감이 잡히지 않습니다.
다만 실습이 성공했는지 파악하는 용도로는 사용이 가능할 것 같습니다.
소스 코드를 컴파일하여 실습을 진행해보겠습니다.
#
R0 레지스터에 0x10000000가 들어간 것을 확인할 수 있고 ...
#
![](https://velog.velcdn.com/images/wbhaao/post/1b776bfa-8e3a-48ab-af46-ccd869cd767a/image.png){:width="600"}
#
R1 레지스터에 0x1780500 값이 저장된 것을 확인할 수 있었습니다.
코드를 작성하여 읽어온 정보를 분석해보겠습니다.
#
_SYS_ID_analysis.py 소스 코드_
```python
data = input("input data : ")
data = int(data,16)

fpga = (data & 0xFF)
arch = (data & 0xF00) >> 8
build = (data & 0xF000) >> 12
hbi = (data & 0xFFF0000) >> 16
rev = (data & 0xF0000000) >> 28

if rev == 0 :
    print("Board revision : Rev A")
elif rev == 1 :
    print("Board revision : Rev B")
elif rev == 2 :
    print("Board revision : Rev C")
else :
    print("rev : {0}".format(rev))

print("hbi board number : {0}".format(hex(hbi)))


if arch == 0x4 :
    print("Bus architecture : AHB")
elif arch == 0x5 :
    print("Bus architecture : AXI")
else : 
    print("Bus : {0}".format(hex(bus)))
```
#
![](https://velog.velcdn.com/images/wbhaao/post/018215bf-6aac-45b2-8d1b-1ad7e5f7d26d/image.png){:width="600"}
#
실행시켜보면 책에서 나온 정보와 일치하는 것을 확인할 수 있습니다.
#
### 3.6 요약
#
코드를 작성하고 하드웨어에서 실행해봤습니다.

제대로 동작하는지 확인해보기 위해 하드웨어의 레지스터에 접근해봤습니다.

결과를 확인하기 위해 gdb도 사용해봤습니다.
#
### 3.7 비고
#
gdb, Make, 링커 스크립트에 대한 간단한 정리가 필요할 것 같습니다.

일단 실습은 계속 진행하면서 시간적으로 여유가 생기면 블로그에 내용을 정리하여 포스트로 올리겠습니다.