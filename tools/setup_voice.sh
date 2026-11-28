#!/bin/bash
# 声の道具（VOICEVOX コア一式）を用意する。局のリポジトリには入れず、VV_HOME（既定 ~/.cache/myradio-voice）に置く。
# 何度実行してもよい（あるものは取り直さない）。すべて GitHub と PyPI から取る。
#   VOICEVOX コア（Python ライブラリ）、VOICEVOX ONNX Runtime、Open JTalk の辞書、音声モデル（.vvm）
# 音声モデルは station.json の voice.model（.vvm の番号）。どの番号にどの声が入っているかは、下の利用規約のページの表にある
# 声の利用規約：https://github.com/VOICEVOX/voicevox_vvm （クレジット「VOICEVOX:<キャラ名>」が必要）
# usage: bash tools/setup_voice.sh
set -euo pipefail
cd "$(dirname "$0")/.."
CORE=0.17.1; ORT=1.23.2
MODEL=$(python3 -c 'import json; print(json.load(open("station.json")).get("voice", {}).get("model", "0"))')
V=${VV_HOME:-$HOME/.cache/myradio-voice}
mkdir -p "$V/vvms"

python3 -c "import voicevox_core" 2>/dev/null || pip install -q --break-system-packages --root-user-action=ignore \
  "https://github.com/VOICEVOX/voicevox_core/releases/download/$CORE/voicevox_core-$CORE-cp310-abi3-manylinux_2_34_x86_64.whl"

if [ ! -e "$V/ort/lib/libvoicevox_onnxruntime.so.$ORT" ]; then
  curl -fsSL -o "$V/ort.tgz" "https://github.com/VOICEVOX/onnxruntime-builder/releases/download/voicevox_onnxruntime-$ORT/voicevox_onnxruntime-linux-x64-$ORT.tgz"
  rm -rf "$V/ort"; mkdir -p "$V/ort"; tar -xzf "$V/ort.tgz" -C "$V/ort" --strip-components=1; rm "$V/ort.tgz"
fi
if [ ! -d "$V/open_jtalk_dic_utf_8-1.11" ]; then
  curl -fsSL -o "$V/dict.tgz" "https://github.com/r9y9/open_jtalk/releases/download/v1.11.1/open_jtalk_dic_utf_8-1.11.tar.gz"
  tar -xzf "$V/dict.tgz" -C "$V"; rm "$V/dict.tgz"
fi
if [ ! -s "$V/vvms/$MODEL.vvm" ]; then
  curl -fsSL -o "$V/vvms/$MODEL.vvm.part" "https://raw.githubusercontent.com/VOICEVOX/voicevox_vvm/$CORE/vvms/$MODEL.vvm"
  mv "$V/vvms/$MODEL.vvm.part" "$V/vvms/$MODEL.vvm"
fi
echo "voice ready: $V (core $CORE, onnxruntime $ORT, model $MODEL.vvm)"
