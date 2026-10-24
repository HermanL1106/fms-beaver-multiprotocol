# FMS Beaver／F4 多協議控制實驗韌體

[English](README.md) · [設定](docs/SETUP.md) · [建置／更新](docs/BUILD.md) · [協議](docs/PROTOCOL.md) · [驗證範圍](docs/VALIDATION.md)

整理 Pocket＋外接 STM32 4IN1 控制一組 FMS F4／Beaver 接收機的逆向成果，提供可重建原始碼、韌體與離線測試。

**目前是地面驗收的 RC1 候選版，不是 FMS 官方協議、上游 MULTI 正式支援或可直接升空的韌體。** 發射功率仍是最低 range-test 晶片設定；航程、實際輻射功率、有 GPS 時失聯／返航均未驗證。

## 相容性與共用身分風險

只驗收本次一組 F4／Beaver。位址與不明身分欄位固定沿用擷取值，**未實作通用對頻或獨立模型身分**；其他接收機可能完全不回應。

**不同人使用相同韌體可能送出相同身分，禁止與另一份相同設定或原廠 F4 同時控制附近相容飛機。** 接收機編號5只是設定檢查，不會產生新 RF 身分。

## 已驗收功能

- 副翼、升降、方向舵與油門；協議內已修正本機方向舵方向。
- 三段模式、長按瞬時按鍵取消 GPS 等待。
- RF 啟用與馬達解鎖分開；低油門解鎖、失敗後須重新切換、不自動恢復。
- 獨立 `FMSBeav` 協議入口。

使用者在 RC1 及恢復 RC1 後均回報舵面、油門正常。這是地面回報，不是飛行或所有故障組合的驗證。

## Pocket 快速設定

先拆槳、拔飛機電池、原廠 F4 關機。韌體刷入**外接高頻頭，不是 Pocket 本體**。
此精簡版只啟用FMSBeav，會取代一般高頻頭的其他協議功能；刷入前先備妥原廠韌體與回復方式。

Internal RF OFF；External RF MULTI，輸出包含CH1–CH16。選FMSBeav／私有編號125，子協議0、接收機編號5、Option42，不勾Bind／Auto bind／Bind CH。
編號125非上游正式分配，可能與其他版本衝突；Option42是啟用鍵，不是固定頻道或微調。

輸出配置：CH1–4 AETR、CH5三段模式、CH7瞬時按鍵、CH8馬達鎖、CH16 RF啟用。
[完整映射與解鎖步驟](docs/SETUP.md)列出本機SC／SE／SD／SA配置；開關名稱不是每台Pocket自動具備的混控。
須自行配置並檢查方向，不提供未驗證的模型匯入檔；方向舵勿未檢查就再次反向。

**RF關閉不是馬達鎖**，可能觸發接收機既有失聯／返航。停馬達使用CH8。
收尾：馬達鎖定、油門最低，先拔飛機電池，再關RF／Pocket；軟體鎖不能代替物理斷電。
本機GPS等待可長按瞬時鍵約3秒取消；空中返航未驗證。沒有真實回傳，因此不顯示假RSSI、假連線或假失聯警告。

## 下載、重建、測試

使用GitHub `v0.1.0-rc1` **Pre-release**或`releases/v0.1.0-rc1/`的韌體；請校驗SHA-256。
[建置文件](docs/BUILD.md)列出固定版本工具鏈與應用程式更新條件，不要猜接線或覆寫未知bootloader。

```sh
python3 scripts/verify.py
sh run-tests.sh
sh scripts/build.sh
```

驗證／測試需要Python3、clang++與ASan／UBSan；重建另需Arduino CLI及multi4in1 STM32F1板套件1.3.1。
上述指令均不會刷機。離線通過不代表航程或飛行安全。

保留原DIY-Multiprotocol-TX-Module授權及作者資訊，本專案依GPLv3-or-later發布。
歡迎回報其他硬體、獨立擷取與可重現地面結果；請勿公開個人憑證或未檢查的完整備份。
