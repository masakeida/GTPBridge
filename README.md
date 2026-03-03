# GTPBridge
A network bridge for GTP (Go Text Protocol) software (like Sabaki)

GTP 対応囲碁 GUI ソフト同士でネットワーク対局を行うための bridge です。2台のPCに Sabaki のような囲碁 GUI ソフトをインストールして、その間で人間対人間、AIエンジン対AIエンジン、人間対AIエンジンで対局が可能です。

対局開始時には、ローカルとリモートの両方の環境で操作が必要です。また、パスと投了を正しく伝達できないため、終局時には別のコミュニケーション手段と操作が必要です。

## 準備

囲碁 GUIソフトとして Sabaki を前提に説明します。PC はネットワークで接続している host-pc と guest-pc があるとします。host-pc の IP アドレスを 192.168.0.31 とします。

bridge_host_guest.py を host-pc にコピーして、bridge_host.py と名前を変更します。ファイル内容は変更しません。
bridge_host_guest.py を guest-pc コピーして、bridge_guest.py と名前を変更します。ファイル内容の8行目を
```
ROLE = "GUEST"
```
と変更し、9行目の
```
SERVER_IP = "192.168.0.31"
```
に host-pc の IP アドレスを記入します。

bridge_host.py の SERVER_IP はなんでもよく、bridge_guest.py の SERVER_IP は host-pc の IP アドレスを入れることに注意してください。これは、host-pc の bridge_host.py が先に起動して待機し、guest-pc の bridge_guest.py は起動と同時に host-pc のIPアドレスに接続をするという動作をするためです。

host-pc と guest-pc にインストールされた Sabaki のエンジンとして、それぞれ bridge_host.py と bridge_guest.py を登録します。
python スクリプトなので、エンジンのパスとして python.exe のフルパス、引数に bridge_host.py もしくは bridge_guest.py のフルパスを入れる設定が簡単です。名前はそれぞれ BridgeHost、BridgeGuest などとしたとして説明していきます。

## 人間 対 人間

host-pc と guest-pc でそれぞれ Sabaki を人間が操作しており、その2人が対局を行う方法です。対局の最初と最後において、お互いのコミュニケーションが必要です。

1. host-pc の Sabaki において [ファイル] -> [新規] を選び、自分の手番と反対側に [エンジンを接続] から [BridgeHost] を選んでください。
2. guest-pc の Sabaki において [ファイル] -> [新規] を選び、自分の手番と反対側に [エンジンを接続] から [BridgeGuest] を選んでください。相手の手番と自分の手番は逆のものでなければなりません。
3. 両方の bridge が接続したことを確認して、白番を持つ側が F10 を押します。これは黒番側のエンジンに対して着手を要求する genmove B というコマンドを発行します。
4. この後、黒番側が最初の着手をすることで対局が開始します。それぞれの Sabaki に相手の着手が表示され、それに対する着手をすることで、対局が進みます。

## AIエンジン 対 AIエンジン

host-pc と guest-pc において動作するAIエンジン (KataGo、pachi、GNU Go 等) 同士が対局する方法です。対局の開始と最後において、人間がそれぞれの Sabaki を操作する必要があります。

1. host-pc の Sabaki において [ファイル] -> [新規] を選び、[エンジンを接続] から host-pc でら動くAIを選びます。AIの手番と反対側に [エンジンを接続] から [BridgeHost] を選んでください。
2. guest-pc の Sabaki において [ファイル] -> [新規] を選び、[エンジンを接続] から guest-pc でら動くAIを選びます。AIの手番と反対側に [エンジンを接続] から [BridgeGuest] を選んでください。相手の手番と自分の手番は逆のものでなければなりません。
3. 両方の bridge が接続したことを確認して、まず白番を持つ側が F5 を押します。これは黒番側のエンジンに対して着手を要求する genmove B というコマンドを発行します。
4. この後、黒番側が F5 を押すことで、最初の着手が行われ、対局が開始します。それぞれの Sabaki に相手の着手が表示され、それに対する着手をすることで、対局が進みます。

## 人間 対 AIエンジン

host-pc において動作するAIエンジン（白番）と guest-pc で操作する人間（黒番）が対局する方法です。対局の開始と最後において、人間がそれぞれの Sabaki を操作する必要があります。AIエンジンを guest-pc、人間を host-pc とする組み合わせも可能です。

1. host-pc の Sabaki において [ファイル] -> [新規] を選び、白番の [エンジンを接続] から host-pc でら動くAIを選びます。黒番の [エンジンを接続] から [BridgeHost] を選んでください。
2. guest-pc の Sabaki において [ファイル] -> [新規] を選び、白番の [エンジンを接続] から [BridgeGuest] を選んでください。
3. 両方の bridge が接続したことを確認して、まず host-pc で F5 を押します。これは黒番側のエンジンに対して着手を要求する genmove B というコマンドを発行します。
4. この後、guest-pc において黒番の人間が最初の着手を行うことで、対局が開始します。それぞれの Sabaki に相手の着手が表示され、それに対する着手をすることで、対局が進みます。

両方の bridge が接続すると、エンジンサイドバーに次のような表示が出ます（ホスト側）。
```
BridgeHost> name 
= NetBridge_HOST
BridgeHost> version 
= 2.2
BridgeHost> protocol_version 
= 2
BridgeHost> list_commands 
= protocol_version
name
version
list_commands
boardsize
clear_board
komi
play
genmove
quit
```

## バグ

パスと投了を正しく相手に伝達できません。
