#!/bin/bash
#
# install-dev-env.sh - Script de Instalação Unificado para o Ambiente CartaOS
#
# Este script instala todas as dependências de sistema e ferramentas de base
# necessárias para desenvolver o CartaOS com a pilha tecnológica moderna.
#

set -euo pipefail

echo "🚀 Iniciando a configuração completa do ambiente de desenvolvimento do CartaOS..."
echo "-------------------------------------------------------------------------"

# --- 1. Dependências de Sistema (APT) ---
echo "📦 [1/4] Instalando pré-requisitos do sistema via APT..."
sudo apt-get update
# Dependências para build, Rust, Tauri (WebKitGTK), Python e OCR
sudo apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    libssl-dev \
    pkg-config \
    libwebkit2gtk-4.1-dev \
    libgtk-3-dev \
    librsvg2-dev \
    python3-pip \
    python3-venv \
    pipx \
    tesseract-ocr \
    poppler-utils \
    unpaper

echo "✅ Pré-requisitos do sistema instalados."
echo "-------------------------------------------------------------------------"

# --- 2. Instalação das Linguagens e Gestores de Pacotes ---
echo "🛠️ [2/4] Instalando Rust (via rustup) e Node.js (via nvm)..."

# Instala Rust se o comando 'cargo' não existir
if ! command -v cargo &> /dev/null; then
    echo "   -> Instalando Rust..."
    # Baixa o instalador do Rust e verifica o checksum antes de executar
    RUSTUP_URL="https://sh.rustup.rs"
    RUSTUP_SCRIPT="rustup-init.sh"
    RUSTUP_EXPECTED_SHA256=$(curl -sSf https://static.rust-lang.org/rustup/release-stable.sha256)
    curl --proto '=https' --tlsv1.2 -sSf "$RUSTUP_URL" -o "$RUSTUP_SCRIPT"
    RUSTUP_ACTUAL_SHA256=$(sha256sum "$RUSTUP_SCRIPT" | awk '{print $1}')
    if [ "$RUSTUP_EXPECTED_SHA256" = "$RUSTUP_ACTUAL_SHA256" ]; then
        sh "$RUSTUP_SCRIPT" -y
        rm "$RUSTUP_SCRIPT"
    else
    NVM_VERSION="v0.39.7"
    NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh"
    NVM_INSTALL_SH="nvm-install.sh"
    NVM_INSTALL_SH_SHA256="b7b2e9e2e5c1e9b4e7c4e8e1d6e2e8e2e5e2e8e2e5e2e8e2e5e2e8e2e5e2e8e2" # Substitua pelo SHA256 real

    curl -fsSL "$NVM_INSTALL_URL" -o "$NVM_INSTALL_SH"
    echo "${NVM_INSTALL_SH_SHA256}  ${NVM_INSTALL_SH}" | sha256sum -c -
    if [ $? -eq 0 ]; then
        bash "$NVM_INSTALL_SH"
        rm "$NVM_INSTALL_SH"
    else
        echo "Erro: O checksum do script de instalação do NVM não confere. Abortando."
        rm "$NVM_INSTALL_SH"
        exit 1
    fi
        rm "$RUSTUP_SCRIPT"
        exit 1
    fi
    # Adiciona o cargo ao PATH da sessão atual
    source "$HOME/.cargo/env"
else
    echo "   -> Rust (cargo) já está instalado."
fi

# Instala nvm se o comando 'nvm' não existir
if ! command -v nvm &> /dev/null; then
    echo "   -> Instalando nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # Carrega o nvm na sessão atual
else
    echo "   -> nvm já está instalado."
fi

# Instala a versão LTS do Node.js se não estiver instalada
if ! nvm list | grep -q "lts"; then
    echo "   -> Instalando a versão LTS do Node.js..."
    nvm install --lts
    nvm use --lts
else
    echo "   -> Versão LTS do Node.js já está instalada."
fi

echo "✅ Linguagens e gestores instalados."
echo "-------------------------------------------------------------------------"

# --- 3. Instalação das Ferramentas de Linha de Comando (CLIs) ---
echo "⚙️ [3/4] Instalando CLIs para Python (Poetry) e Tauri..."

# Instala Poetry via pipx
if ! command -v poetry &> /dev/null; then
    echo "   -> Instalando Poetry..."
    pipx install poetry
else
    echo "   -> Poetry já está instalado."
fi

# Instala Tauri CLI via cargo
if ! command -v tauri &> /dev/null; then
    echo "   -> Instalando Tauri CLI..."
    cargo install tauri-cli
else
    echo "   -> Tauri CLI já está instalada."
fi

echo "✅ CLIs instaladas."
echo "-------------------------------------------------------------------------"

# --- 4. Finalização ---
echo "🎉 [4/4] Ambiente de desenvolvimento base configurado com sucesso!"
echo ""
echo "IMPORTANTE: Para garantir que todos os comandos estejam disponíveis,"
echo "recomendamos que você feche e reabra seu terminal antes de continuar."
echo "Como alternativa, execute: source ~/.bashrc"
