#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法：bash scripts/git-identity.sh [github|codeup|show]

  github  使用 DDiabolous <1689902663@qq.com>
  codeup  使用原来的 zzw Codeup 身份
  show    显示当前仓库的提交身份（默认）

在目标仓库内执行；仅修改该仓库配置，不修改全局配置或历史提交。
EOF
}

case "${1:-show}" in
  github|codeup|show) action="${1:-show}" ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 1 ;;
esac

if [[ $# -gt 1 ]]; then
  usage >&2
  exit 1
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo '错误：请在目标 Git 仓库中执行。' >&2
  exit 1
fi

case "$action" in
  github)
    git config --local user.name 'DDiabolous'
    git config --local user.email '1689902663@qq.com'
    ;;
  codeup)
    git config --local user.name 'zzw'
    git config --local user.email '940b129c-6a2f-4f5e-972d-79fb82065318-zhangzhengwei_winsrobot@noreply.codeup.aliyun.com'
    ;;
esac

echo "仓库：$(git rev-parse --absolute-git-dir)"
echo "姓名：$(git config --get user.name || true)"
echo "邮箱：$(git config --get user.email || true)"
echo '此脚本仅切换提交署名；推送认证不受影响。'
