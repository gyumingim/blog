---
id: 13
title: "임베디드 OS 프로젝트 Ch.1"
subtitle: "개발 환경 구성하기"
date: "2025.03.26"
thumbnail: "EmbeddedOS1.png"
---
<img src="../../static/image/EmbeddedOS1.png" height="200">

#
## 시작하기 전
#
[임베디드 OS 개발 프로젝트](https://www.yes24.com/Product/Goods/84909414)를 통해 공부한 내용을 블로그에 기록하려고 합니다.
#
## 2.1 컴파일러 설치하기 
#
gcc-arm-none-eabi 패키지와 관련 패키지들을 설치했습니다.
#
```shell
sudo apt-get update
sudo apt-get install gcc-arm-none-eabi

arm-none-eabi-gcc -v
```
#
위 명령어를 입력하여 설치가 완료되었는지 확인해줍니다.
#

![](https://velog.velcdn.com/images/wbhaao/post/eb153653-82dd-41d4-9351-a3a0bf68c2e0/image.png){:height="300px"}

#
### 2.2 QEMU 설치하기
#
qemu-system-arm 패키지와 관련 패키지를 설치했습니다.
#
```shell
sudo apt-get update
sudo apt-get install qemu-system-arm

qemu-system-arm -M ?
```
#
위 명령어를 입력하여 QEMU가 어떤 ARM 시스템을 에뮬레이트할 수 있는지 확인했습니다.