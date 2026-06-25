#!/bin/bash
# 部署到 Hugging Face Spaces
# 先手动去 huggingface.co 创建 Space（SDK 选 Streamlit）
# 然后复制 Space 的 git URL 到下面
set -e

echo "=== 高考志愿 资料收集 → Hugging Face Spaces ==="
echo ""
echo "还没注册？先去 https://huggingface.co/ 注册账号"
echo "然后点右上角头像 → New Space"
echo "  Space Name: 随便填（如 gaokao-collector）"
echo "  SDK: 选 Streamlit"
echo "  可见性: Public（客户才能访问）"
echo "点 Create Space"
echo ""
echo "创建完后把下面的 git 地址贴给我："
read -p "HF Space Git URL (如 https://huggingface.co/spaces/你的名字/gaokao-collector): " HF_URL

if [ -z "$HF_URL" ]; then
    echo "取消"
    exit 1
fi

cd "$(dirname "$0")"
git init
git add app.py requirements.txt README.md
git commit -m "init: 考生资料收集表"
git remote add origin "$HF_URL"
git push --set-upstream origin main

echo ""
echo "部署成功！"
echo "等 2-3 分钟构建完成后，访问 https://$HF_URL 即可使用"
echo "以后更新代码：cd hf_deploy && git add . && git commit -m 'update' && git push"
