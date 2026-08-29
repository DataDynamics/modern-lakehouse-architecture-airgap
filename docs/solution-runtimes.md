# 솔루션별 동작 환경과 배포 방식

각 솔루션이 **어디에서 도는지**와 **어떻게 배포하는지**를 공식 문서 기준으로 정리한
문서입니다. 제품이 제공하는 기능은 [solution-features.md](solution-features.md),
아키텍처에서의 역할은 [solutions.md](solutions.md)를 참고하십시오.

> **버전 주의** 아래 수치와 지원 목록은 확인 시점(2026-08)의 문서 기준입니다. Cloudera
> 제품은 릴리스마다 지원 OS·Kubernetes 버전이 바뀌므로, **실제 반입할 릴리스의 Support
> Matrix로 반드시 재확인**해야 합니다. 이 문서는 배포 형태의 큰 그림을 잡는 용도입니다.

## 목차

- [요약](#요약)
- [Cloudera CDP — Base 클러스터](#cloudera-cdp--base-클러스터)
- [Cloudera CFM — 두 가지 배포 경로](#cloudera-cfm--두-가지-배포-경로)
  - [경로 A — Base 클러스터 위 (parcel + CSD)](#경로-a--base-클러스터-위-parcel--csd)
  - [경로 B — CFM Operator for Kubernetes](#경로-b--cfm-operator-for-kubernetes)
- [Cloudera CDE · Cloudera AI — Kubernetes 전용](#cloudera-cde--cloudera-ai--kubernetes-전용)
  - [Kubernetes 기반 선택](#kubernetes-기반-선택)
  - [ECS 호스트 요건](#ecs-호스트-요건)
  - [스토리지 프로비저너](#스토리지-프로비저너)
- [MinIO AIStor](#minio-aistor)
  - [배포 대상](#배포-대상)
  - [Kubernetes 배포](#kubernetes-배포)
  - [하드웨어 요건](#하드웨어-요건)
- [Starburst Enterprise](#starburst-enterprise)
  - [배포 방식](#배포-방식)
  - [공통 요건](#공통-요건)
  - [Kubernetes 배포 요건](#kubernetes-배포-요건)
- [Spotfire](#spotfire)
  - [구성요소별 실행 환경](#구성요소별-실행-환경)
  - [운영체제 (14.6 LTS 기준, 64비트만)](#운영체제-146-lts-기준-64비트만)
  - [데이터베이스](#데이터베이스)
  - [컨테이너 배포](#컨테이너-배포)
- [폐쇄망 배포 시 공통 고려사항](#폐쇄망-배포-시-공통-고려사항)
  - [반입 채널이 제품마다 다릅니다](#반입-채널이-제품마다-다릅니다)
  - [Cloudera Data Services 반입에서 특히 유의할 점](#cloudera-data-services-반입에서-특히-유의할-점)
  - [그 밖에 준비해야 할 것](#그-밖에-준비해야-할-것)
- [노드 그룹 정리](#노드-그룹-정리)
- [확인이 필요한 항목](#확인이-필요한-항목)
- [출처](#출처)
- [용어집](#용어집)
  - [배포 형태](#배포-형태)
  - [Cloudera 배포](#cloudera-배포)
  - [스토리지와 인프라](#스토리지와-인프라)
  - [폐쇄망 반입](#폐쇄망-반입)
  - [기타](#기타)

## 요약

| 솔루션 | 베어메탈 · VM | 컨테이너 · Kubernetes | 배포 도구 |
|---|---|---|---|
| Cloudera CDP (Base) | ● 기본 | － | Cloudera Manager (parcel · CSD) |
| Cloudera CFM | ● Base 클러스터 위 | ● CFM Operator | Cloudera Manager 또는 K8s Operator |
| Cloudera CDE | － | ● 전용 | Data Services (OpenShift 또는 ECS) |
| Cloudera AI | － | ● 전용 | Data Services (OpenShift 또는 ECS) |
| MinIO AIStor | ● Linux | ● Operator | Helm / 패키지 |
| Starburst Enterprise | ● Starburst Admin | ● Helm | Helm 또는 Starburst Admin |
| Spotfire | ● 기본 | ● Cloud Deployment Kit | 설치 프로그램 또는 Helm |

**가장 중요한 구분은 Cloudera 제품군이 두 갈래로 나뉜다는 점입니다.**

| 구분 | 대상 | 실행 기반 |
|---|---|---|
| Cloudera Base (구 CDP Private Cloud Base) | Kafka, ZooKeeper, SMM, NiFi | 베어메탈 또는 VM 위의 리눅스 호스트 |
| Cloudera Data Services | CDE, Cloudera AI | Kubernetes (OpenShift 또는 ECS) |

즉 이 아키텍처를 구축하면 **성격이 다른 두 종류의 클러스터를 함께 운영**하게 됩니다.
Layer 3(Kafka)은 리눅스 호스트 클러스터에, Layer 5(CDE)와 모델 서빙(Cloudera AI)은
Kubernetes에 놓입니다.

---

## Cloudera CDP — Base 클러스터

문서: [Operating System Requirements](https://docs.cloudera.com/cdp-private-cloud-base/7.3.1/cdp-private-cloud-base-installation/topics/cdpdc-os-requirements.html) ·
[Installation Guide](https://docs.cloudera.com/cdp-private-cloud-base/7.1.9/installation/index.html)

이 아키텍처에서 Kafka · ZooKeeper · Streams Messaging Manager가 올라가는 기반입니다.

| 항목 | 내용 |
|---|---|
| 배포 대상 | **베어메탈 또는 가상 머신 모두 지원** |
| 컨테이너 | 해당 없음. Base 클러스터는 호스트에 직접 설치합니다 |
| 운영체제 | Linux만 지원. Red Hat Enterprise Linux(및 호환), Ubuntu, SLES |
| 배포 방식 | Cloudera Manager가 parcel과 CSD로 각 호스트에 배포·관리 |
| 파일시스템 | ext3 또는 ext4 권장 (HDFS 검증 기준) |
| 선행 패키지 | `iproute`, `rpcbind`(`rpcinfo`) — Cloudera Manager Agent가 도는 모든 호스트 |

**베어메탈과 VM의 선택 기준**은 Kafka의 디스크 I/O입니다. 브로커는 로그 세그먼트를
순차 기록하므로 스토리지 지연에 민감하고, 공유 스토리지 기반 VM에서는 성능 편차가
발생할 수 있습니다. 금융권 실시간 요건이 초 단위라면 브로커만이라도 로컬 디스크를 쓰는
구성을 검토할 만합니다.

---

## Cloudera CFM — 두 가지 배포 경로

문서: [Installing CFM parcel and CSD files](https://docs.cloudera.com/cfm/2.1.5/deployment/topics/cfm-add-parcel-url.html) ·
[CFM Operator for Kubernetes](https://docs.cloudera.com/cfm-operator/2.11.0/index.html)

CFM은 **선택지가 두 개**라는 점이 다른 제품과 다릅니다.

### 경로 A — Base 클러스터 위 (parcel + CSD)

| 항목 | 내용 |
|---|---|
| 실행 기반 | Cloudera Base 클러스터의 리눅스 호스트 (베어메탈 · VM) |
| 배포 | Cloudera Manager에 CFM parcel URL을 추가하고, NiFi·NiFi Registry CSD 파일을 CSD 디렉터리에 업로드 |
| 관리 | Cloudera Manager에서 다른 서비스와 동일하게 기동·모니터링 |

Kafka와 같은 클러스터에 두면 Cloudera Manager 하나로 통합 관제할 수 있습니다. 전통적인
구성입니다.

### 경로 B — CFM Operator for Kubernetes

| 항목 | 내용 |
|---|---|
| 실행 기반 | Kubernetes |
| 배포 대상 | Apache NiFi 클러스터(단일 노드 또는 분산), NiFi Registry |
| 특징 | NiFi 1.x와 2.x를 동시에 운영 가능. CR(Custom Resource)로 클러스터 정의 |
| 배포 아티팩트 | Cloudera Docker 레지스트리와 Cloudera Archive. **양쪽 모두 Cloudera 자격증명 필요** |

**선택 기준에 대한 의견** — 흐름 수가 많고 팀별로 격리가 필요하면 Operator 방식이
유리합니다. 반대로 운영 인력이 Cloudera Manager에 익숙하고 Kubernetes 운영 경험이
얕다면 경로 A가 안전합니다. 폐쇄망에서는 두 경로 모두 반입 절차가 필요하지만, 경로 B는
컨테이너 이미지까지 미러링해야 하므로 준비 항목이 하나 더 늘어납니다.

---

## Cloudera CDE · Cloudera AI — Kubernetes 전용

문서: [Installing Cloudera Data Services (ECS)](https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation-ecs/topics/cdppvc-installation-ecs-steps.html) ·
[Prerequisites for CDE on premises](https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation-ecs/topics/cde-private-cloud-prereqs.html) ·
[Requirements for Cloudera AI on OpenShift](https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation/topics/ml-pvc-requirements.html)

두 제품 모두 Cloudera Data Services에 속하며 **Kubernetes 위에서만 동작합니다.**
베어메탈·VM에 직접 설치하는 경로는 없습니다.

### Kubernetes 기반 선택

| 방식 | 설명 | 부담 |
|---|---|---|
| OpenShift Container Platform | 고객이 Kubernetes 인프라를 직접 배포·운영 | OpenShift 라이선스와 운영 역량 필요 |
| Cloudera Embedded Container Service (ECS) | Cloudera Manager가 내장 Kubernetes를 구성·관리 | 호스트만 제공하면 됨 |

**ECS는 "호스트만 주면 Cloudera Manager가 Kubernetes를 만들어 준다"는 것이 핵심**입니다.
Kubernetes 운영 조직이 따로 없는 금융권 현장에서는 ECS 쪽이 현실적인 경우가 많습니다.

### ECS 호스트 요건

| 항목 | 내용 |
|---|---|
| `/var/lib` 여유 공간 | 설치 시점에 **모든 호스트가 300 GiB 초과** |
| Docker 스토리지 | 최소 300 GiB |
| `nfs-utils` | Cloudera AI의 longhorn-nfs 마운트를 위해 **모든 노드에 필요** |

### 스토리지 프로비저너

| 플랫폼 | 기본 프로비저너 |
|---|---|
| OpenShift | CephFS |
| ECS | Longhorn |

Cloudera AI는 추가로 다음을 요구합니다.

| 항목 | 내용 |
|---|---|
| NFS | **NFS 4.1** — 프로젝트 파일·폴더 저장용. 내부(권장) 또는 외부 NFS 서버 |
| 볼륨 | 내부 NFS 서버에 RWO 영구 볼륨을 할당해 RWX 볼륨을 제공 |
| 스토리지 클래스 | OpenShift 기준 `ocs-storagecluster-cephfs`(CephFS)와 기본 블록 스토리지 클래스 필요 |
| 용량 | 워크벤치당 사용자 파일 1 TB. 외부 NFS 최소 1800 GiB, 내부 NFS 최소 3800 GiB(복제 계수 2 포함) |

> **설계 확인 필요** CDE 온프레미스 문서는 Base 클러스터에 **Apache Ozone 서비스가
> 활성화되어 있어야 환경을 생성할 수 있다**고 기술합니다. 이 아키텍처는 오브젝트
> 스토리지로 MinIO를 선택했으므로, Ozone이 별도로 필요한지(메타데이터·중간 산출물
> 용도인지, 데이터 저장까지 포함하는지)를 반입 버전 문서로 확인해야 합니다. 필요하다면
> Ozone 클러스터 용량이 산정에서 누락되지 않도록 해야 합니다.

**GPU** — 모델 서빙에 GPU가 필요하지만 확인한 요건 페이지에는 GPU 항목이 없었습니다.
GPU 노드 사양과 드라이버·operator 요건은 별도 문서로 확인이 필요합니다.

---

## MinIO AIStor

문서: [Installation](https://docs.min.io/aistor/installation/) ·
[Hardware and System Requirements](https://docs.min.io/aistor/reference/aistor-server/requirements/) ·
[Deploy on Kubernetes](https://docs.min.io/aistor/installation/kubernetes/install/deploy-aistor-on-kubernetes/) ·
[Deploy with a Private Container Registry](https://docs.min.io/enterprise/aistor-object-store/installation/kubernetes/install/deploy-aistor-private-registry/)

### 배포 대상

| 플랫폼 | 용도 |
|---|---|
| Kubernetes (upstream) | **운영** |
| Red Hat OpenShift | **운영** (인증된 operator 제공) |
| Linux — RHEL, Ubuntu Server | **운영** |
| 컨테이너 (Docker Compose 등) | 개발·평가 |
| macOS · Windows | 개발·평가 |

문서는 macOS · Windows · 컨테이너 호스트를 "로컬 개발과 평가용"으로 명시합니다. 운영은
**Kubernetes 또는 Linux 직접 설치** 두 갈래입니다.

### Kubernetes 배포

| 항목 | 내용 |
|---|---|
| 방식 | 1st-party Operator (Kubernetes Operator 패턴) |
| Helm | 3.17 이상 권장 |
| 권한 | CRD · StatefulSet · Secret을 여러 네임스페이스에 생성할 수 있는 광범위한 권한 필요 |
| Operator 역할 | 파드 스케줄링, 설정 관리, 인증서 교체, 업그레이드 오케스트레이션 |
| 이미지 | 노드 아키텍처와 일치해야 함 (명령을 실행하는 장비 기준이 아님) |

### 하드웨어 요건

| 항목 | 내용 |
|---|---|
| CPU | 노드당 **물리 코어 8개 이상 권장**. 그 이하는 동시 S3 부하에서 병목 |
| 스토리지 | 전 구간 플래시(NVMe 또는 SSD) 권장. 고성능 요건은 NVMe |
| 파일시스템 | **XFS 필수** — 성능과 일관성 보장을 위해 요구됩니다 |
| Erasure Coding | 최소 드라이브 2개. 기본 erasure set은 드라이브 2~16개 |
| 패리티 | **운영은 EC:3 이상 필수.** 그 미만은 개발·테스트용 |
| 단일 노드·단일 드라이브 | 이중화 없음. 비운영 테스트·평가 전용 |
| 노드 동질성 | 풀 내 모든 노드의 CPU·메모리·메인보드·스토리지 어댑터와 OS·커널 설정을 일치시킬 것 |

> **파일시스템 주의** Cloudera Base는 ext3/ext4를 권장하고 MinIO는 XFS를 요구합니다.
> **두 노드 그룹의 파일시스템 표준이 다르므로**, 서버 프로비저닝 표준을 하나로 강제하면
> 한쪽이 요건을 벗어납니다. 노드 그룹별로 나눠 정의해야 합니다.

용량 산정은 MinIO의 Erasure Code Calculator로 호스트·드라이브 수를 잡는 것이 문서의
안내입니다.

---

## Starburst Enterprise

문서: [Deployment basics](https://docs.starburst.io/latest/installation/deployment.html) ·
[Plan your Kubernetes deployment](https://docs.starburst.io/latest/k8s/requirements.html) ·
[Deploy with Kubernetes](https://docs.starburst.io/latest/k8s.html)

### 배포 방식

| 방식 | 대상 | 비고 |
|---|---|---|
| Kubernetes + Helm 차트 | 컨테이너 | 문서가 권장하는 운영 방식 |
| **Starburst Admin** | **베어메탈 · 가상 머신** | 문서상 베어메탈·VM에는 이 도구가 **필수** |
| Docker 단독 | 평가용 | 문서가 **운영·PoC 용도로 사용하지 말 것**을 명시 |

### 공통 요건

| 항목 | 내용 |
|---|---|
| 운영체제 | **RHEL. 다른 리눅스 배포판은 공식 지원 대상이 아님** |
| Java | 64비트 Java 25 (최소 25.0.2) |
| CPU 아키텍처 | x86_64 (AMD64) 또는 AArch64 (ARM64) |
| 네트워크 | 클러스터 내부 최소 10 Gbps. 오브젝트 스토리지와는 25 Gbps 이상 권장 |
| 메모리 | 가용 메모리의 70~85%를 할당. 운영 클러스터는 32 GB 초과 할당 권장 |
| 구성 | Coordinator 전용 노드 1대 + Worker 다수 |

### Kubernetes 배포 요건

| 항목 | 내용 |
|---|---|
| Kubernetes 버전 | 1.26 ~ 1.35 |
| 검증 배포판 | EKS, GKE, AKS, **Red Hat OpenShift**, **Rancher RKE2** |
| 노드 사양 | 노드당 RAM 64~256 GB, 코어 16~64 |
| 노드 정책 | **모든 노드가 동일해야 하며, 노드 하나에 Worker 또는 Coordinator 하나만 배치.** 다른 애플리케이션과 공유 불가 |
| 도구 | `kubectl`, Helm 3.2.4 이상 |
| 백엔드 DB | **외부에서 관리하는 데이터베이스 필수** (backend service용) |
| 이미지·차트 | `harbor.starburstdata.net`. 고객 전용 Harbor 계정을 Starburst 지원팀에서 발급 |

> **용량 산정에 영향** "노드 하나당 Worker 하나"는 일반적인 Kubernetes 수평 확장과
> 다릅니다. Worker를 늘리려면 **노드 자체를 추가**해야 하므로, 기존 노드에 파드를 더
> 채우는 방식으로 계산하면 용량이 어긋납니다. 오토스케일도 노드 단위로 동작합니다.

폐쇄망에서는 OpenShift 또는 RKE2가 현실적인 선택지이고, Base 클러스터와 별개로 이미
Cloudera Data Services용 Kubernetes가 존재한다면 **같은 클러스터에 얹을지 분리할지**를
정해야 합니다. Starburst가 노드 전용 점유를 요구하므로 노드 풀은 어차피 분리됩니다.

---

## Spotfire

문서: [Spotfire Server 14.6 LTS System Requirements](https://docs.tibco.com/pub/spotfire/general/sr/sr/topics/spotfire_server_14_6.html) ·
[Node manager installation](https://docs.tibco.com/pub/spotfire_server/latest/doc/html/TIB_sfire_server_tsas_admin_help/server/topics/node_manager_installation.html) ·
[Spotfire Cloud Deployment Kit](https://github.com/spotfiresoftware/spotfire-cloud-deployment-kit)

### 구성요소별 실행 환경

| 구성요소 | 실행 환경 |
|---|---|
| Spotfire Server | Windows Server 또는 Linux |
| Node Manager | Windows Server 또는 Linux. **Spotfire Server와 같은 장비에 설치 금지** |
| Spotfire 데이터베이스 | Oracle, SQL Server, PostgreSQL 중 하나 |

### 운영체제 (14.6 LTS 기준, 64비트만)

| 계열 | 지원 버전 |
|---|---|
| Windows Server | 2025, 2022, 2019 |
| Red Hat Enterprise Linux | 10, 9 |
| Ubuntu | 24.04 LTS, 22.04 LTS |
| Debian | 13, 12 |

Java는 Eclipse Temurin 21 LTS가 설치본에 포함됩니다.

### 데이터베이스

| 제품 | 지원 버전 |
|---|---|
| Oracle | 26, 23, 19 (RAC 포함) |
| SQL Server | 2025, 2022, 2019 (Express는 비운영 전용) |
| PostgreSQL | 18, 17, 16, 15 |

> **중요한 제약** Node Manager는 OS에 따라 실행할 수 있는 서비스가 다릅니다.
>
> | Node Manager | 실행 가능 서비스 |
> |---|---|
> | **Windows** | Web Player, Automation Services, TERR, Python |
> | **Linux** | **TERR와 Python만** |
>
> 즉 **Spotfire Web Player를 쓰려면 Windows Server 노드가 필요합니다.** 이 아키텍처의
> 대시보드 소비는 Web Player 기반이므로, 리눅스 일색으로 구성하려던 계획이 있다면 이
> 지점에서 어긋납니다. 금융권 표준 OS 정책과 충돌할 수 있어 초기에 확인해야 합니다.

### 컨테이너 배포

Spotfire는 컨테이너 이미지와 Helm 차트를 만드는 **Cloud Deployment Kit**를 제공합니다.
인증된 Kubernetes 배포판(1.24 이상)과 Helm 3 이상이 필요합니다. 운영 환경에서는 서비스
종류별로 물리 서버·VM·컨테이너 중 **각각 전용 장비에 분리 배치**할 것을 권고합니다.

---

## 폐쇄망 배포 시 공통 고려사항

문서: [Installing in Air Gap environment](https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation/topics/cdppvc-installation-airgap.html) ·
[Configuring Local Package and Parcel Repositories](https://docs.cloudera.com/cdp-private-cloud-base/7.1.9/installation/topics/cdpdc-local-package-parcel-repositories.html)

### 반입 채널이 제품마다 다릅니다

| 제품 | 반입 대상 | 비고 |
|---|---|---|
| Cloudera Base | parcel, CSD, OS 패키지 | 사내 HTTP 서버에 로컬 저장소 구성 |
| Cloudera Data Services | 컨테이너 이미지 + 아카이브 | 사내 Docker 레지스트리 |
| CFM Operator | 컨테이너 이미지 + 아카이브 | Cloudera 자격증명 필요 |
| MinIO AIStor | 컨테이너 이미지 또는 리눅스 패키지 | 사설 레지스트리 배포 절차 제공 |
| Starburst | Helm 차트 + Docker 이미지 | Harbor(`harbor.starburstdata.net`) 미러링 |
| Spotfire | 설치 프로그램 또는 컨테이너 이미지 | |

### Cloudera Data Services 반입에서 특히 유의할 점

| 항목 | 내용 |
|---|---|
| 용량 | 배포물이 **약 500 GB**. 다운로드 전 여유 공간 확보 필요 |
| 소요 시간 | 이미지 복사에 **4~5시간** 소요될 수 있음 |
| 레지스트리 | **TLS가 적용된 사설 Docker 레지스트리만 지원.** 자체 서명 또는 사설·공인 CA 서명 인증서 필요 |
| 설정 | `[레지스트리]/[리포지터리]` 형식으로 Custom Docker Repository 지정 |

**반입 일정은 과소평가하기 쉬운 항목입니다.** 500 GB 이관과 4~5시간의 이미지 복사는
1회가 아니라 버전 업그레이드마다 반복됩니다. 정기 패치 주기를 설계할 때 이 시간을
포함해야 합니다.

### 그 밖에 준비해야 할 것

- **한글 폰트** — 다이어그램·리포트 렌더링과 PDF 출력에 필요합니다
- **사내 NTP·DNS** — Kerberos와 TLS 인증서 검증이 시간·이름 해석에 의존합니다
- **OS 패키지 저장소** — `iproute`, `rpcbind`, `nfs-utils`, `xfsprogs` 등 선행 패키지
- **모델 파일** — 고객 보유 모델의 가중치 반입 절차 (
  [agent-readiness-analysis.md](agent-readiness-analysis.md) 참고)

---

## 노드 그룹 정리

배포 형태가 다른 구성요소를 묶으면 다음과 같이 나뉩니다. 서버 산정과 OS 표준을 정할 때의
기준선입니다.

| 노드 그룹 | 구성요소 | 실행 형태 | 파일시스템 |
|---|---|---|---|
| A. Base 클러스터 | Kafka, ZooKeeper, SMM, (CFM 경로 A) | 베어메탈 · VM | ext3 / ext4 |
| B. Data Services K8s | CDE(Spark·Airflow), Cloudera AI, (CFM 경로 B) | Kubernetes | 프로비저너 관리 |
| C. 오브젝트 스토리지 | MinIO AIStor | Linux 또는 K8s | **XFS** |
| D. 질의 엔진 | Starburst Coordinator · Worker | K8s 전용 노드 또는 VM | － |
| E. BI | Spotfire Server, Node Manager | **Web Player는 Windows** | － |
| F. 모델 서빙 | Cloudera AI Inference (GPU 노드) | Kubernetes | － |

**그룹 B와 D를 같은 Kubernetes 클러스터에 둘지**가 결정 사항입니다. Starburst가 노드
전용 점유를 요구하므로 노드 풀은 어차피 분리되며, 클러스터를 합치면 관리 지점이 줄고
나누면 장애 격리가 좋아집니다.

## 확인이 필요한 항목

| # | 항목 | 이유 |
|---|---|---|
| 1 | 반입 릴리스의 Support Matrix | OS·Kubernetes 지원 버전은 릴리스마다 다름 |
| 2 | CDE의 Ozone 선행 요건 | MinIO를 쓰는 구성에서 Ozone이 별도로 필요한지 |
| 3 | Cloudera AI GPU 노드 요건 | 확인한 요건 문서에 GPU 항목이 없었음 |
| 4 | Spotfire Web Player의 Windows 필요성 | 리눅스 표준 정책과 충돌 여부 |
| 5 | Starburst 노드 전용 점유 기준의 용량 산정 | 파드 단위가 아닌 노드 단위 증설 |
| 6 | Kubernetes 클러스터 통합 여부 | Data Services와 Starburst를 합칠지 분리할지 |
| 7 | Starburst의 RHEL 한정 지원 | 베어메탈·VM 경로 선택 시 OS 표준 |
| 8 | 정기 패치 시 반입 소요 시간 | 500 GB · 4~5시간이 업그레이드마다 반복 |

---

## 출처

확인 시점: 2026-08

**Cloudera Base**
- https://docs.cloudera.com/cdp-private-cloud-base/7.3.1/cdp-private-cloud-base-installation/topics/cdpdc-os-requirements.html
- https://docs.cloudera.com/cdp-private-cloud-base/7.1.9/installation/index.html
- https://docs.cloudera.com/cdp-private-cloud-base/7.1.9/installation/topics/cdpdc-local-package-parcel-repositories.html

**Cloudera CFM**
- https://docs.cloudera.com/cfm/2.1.5/deployment/topics/cfm-add-parcel-url.html
- https://docs.cloudera.com/cfm-operator/2.11.0/index.html

**Cloudera Data Services (CDE · Cloudera AI)**
- https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation-ecs/topics/cdppvc-installation-ecs-steps.html
- https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation-ecs/topics/cde-private-cloud-prereqs.html
- https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation/topics/ml-pvc-requirements.html
- https://docs.cloudera.com/cdp-private-cloud-data-services/latest/installation/topics/cdppvc-installation-airgap.html
- https://docs.cloudera.com/cdp-private-cloud-data-services/latest/managing-ecs/topics/cm-manage-experiences-compute-service.html

**MinIO AIStor**
- https://docs.min.io/aistor/installation/
- https://docs.min.io/aistor/reference/aistor-server/requirements/
- https://docs.min.io/aistor/installation/kubernetes/install/deploy-aistor-on-kubernetes/
- https://docs.min.io/aistor/installation/kubernetes/install/deploy-aistor-on-openshift/

**Starburst Enterprise**
- https://docs.starburst.io/latest/installation/deployment.html
- https://docs.starburst.io/latest/k8s/requirements.html
- https://docs.starburst.io/latest/k8s.html

**Spotfire**
- https://docs.tibco.com/pub/spotfire/general/sr/sr/topics/spotfire_server_14_6.html
- https://docs.tibco.com/pub/spotfire_server/latest/doc/html/TIB_sfire_server_tsas_admin_help/server/topics/node_manager_installation.html
- https://github.com/spotfiresoftware/spotfire-cloud-deployment-kit

---

## 용어집

이 문서에 등장하는 용어입니다. 아키텍처 전반의 용어는 [architecture.md](architecture.md),
제품 기능 용어는 [solution-features.md](solution-features.md)의 용어집을 참고하십시오.

### 배포 형태

| 용어 | 설명 |
|---|---|
| 베어메탈 | 가상화 계층 없이 물리 서버에 운영체제를 직접 올려 쓰는 구성 |
| VM (가상 머신) | 하이퍼바이저 위에 만든 가상 서버 |
| 컨테이너 | 애플리케이션과 의존성을 함께 묶어 격리 실행하는 단위 |
| Kubernetes | 컨테이너의 배치·확장·복구를 자동화하는 오케스트레이션 플랫폼 |
| OpenShift | Red Hat의 상용 Kubernetes 배포판 |
| RKE2 | Rancher의 Kubernetes 배포판 |
| Operator | CR로 정의한 상태를 유지하도록 설치·설정·업그레이드를 자동화하는 Kubernetes 확장 |
| CR (Custom Resource) | Kubernetes에 사용자가 정의해 추가하는 리소스 유형 |
| Helm · Helm 차트 | Kubernetes 배포물의 패키지 관리자와 그 패키지 |
| StatefulSet | 상태를 가지는 파드를 순서와 고정 식별자로 관리하는 Kubernetes 워크로드 |
| 노드 풀 | 같은 사양·역할로 묶은 Kubernetes 노드 그룹 |

### Cloudera 배포

| 용어 | 설명 |
|---|---|
| Cloudera Manager | Cloudera 클러스터의 설치·설정·모니터링을 담당하는 관리 도구 |
| parcel | Cloudera Manager가 호스트에 배포하는 바이너리 패키지 형식 |
| CSD (Custom Service Descriptor) | 새 서비스를 Cloudera Manager가 인식·관리하도록 기술한 정의 파일 |
| Cloudera Base | 리눅스 호스트에 직접 설치하는 Cloudera 기반 클러스터 |
| Cloudera Data Services | Kubernetes 위에서 동작하는 Cloudera 서비스군 (CDE, Cloudera AI 등) |
| ECS (Embedded Container Service) | Cloudera Manager가 구성·관리하는 내장 Kubernetes |
| Longhorn | ECS의 기본 블록 스토리지 프로비저너 |
| CephFS | OpenShift 환경에서 쓰이는 분산 파일시스템 프로비저너 |
| Apache Ozone | Cloudera의 분산 오브젝트 스토리지 |

### 스토리지와 인프라

| 용어 | 설명 |
|---|---|
| XFS · ext3 · ext4 | 리눅스 파일시스템. MinIO는 XFS를, Cloudera Base는 ext3/ext4를 요구·권장합니다 |
| NVMe · SSD | 플래시 기반 저장 장치. NVMe가 더 낮은 지연을 제공합니다 |
| Erasure Coding | 데이터를 조각과 패리티로 분산 저장해 장애를 견디는 보호 방식 |
| Erasure Set | 패리티를 함께 계산하는 드라이브 묶음 |
| 패리티 (EC:n) | 동시에 잃어도 복구 가능한 조각 수. 운영은 EC:3 이상 |
| NFS 4.1 | 네트워크 파일 공유 프로토콜 버전. Cloudera AI가 요구합니다 |
| RWO · RWX | 각각 한 노드만 읽기·쓰기 가능한 볼륨과, 여러 노드가 동시에 가능한 볼륨 |
| 스토리지 클래스 | Kubernetes에서 볼륨을 어떤 스토리지로 만들지 정의한 유형 |
| 프로비저너 | 스토리지 클래스 요청에 따라 실제 볼륨을 만드는 구성요소 |

### 폐쇄망 반입

| 용어 | 설명 |
|---|---|
| 로컬 저장소 (local repository) | 외부 저장소를 사내에 복제해 둔 패키지·parcel 서버 |
| 사설 컨테이너 레지스트리 | 사내에 두는 컨테이너 이미지 저장소. Cloudera는 TLS 적용을 요구합니다 |
| 미러링 | 외부 저장소의 내용을 사내로 복제하는 작업 |
| Harbor | Starburst가 배포 아티팩트를 제공하는 컨테이너 레지스트리 |
| Support Matrix | 제품 릴리스별 지원 OS·플랫폼·버전을 정리한 공식 표 |

### 기타

| 용어 | 설명 |
|---|---|
| Coordinator · Worker | Trino에서 질의를 계획·분배하는 노드와 실제 연산을 수행하는 노드 |
| Node Manager | Spotfire 서비스를 실제로 실행하는 구성요소 |
| Web Player | 브라우저에서 Spotfire 분석을 보고 조작하게 하는 서비스 |
| TERR | Spotfire의 R 실행 엔진 |
| Automation Services | Spotfire의 작업 자동화 서비스 |
| RAC | Oracle Real Application Clusters. 여러 인스턴스로 구성하는 고가용성 방식 |
