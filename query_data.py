#!/usr/bin/env python3
"""查询大数据平台数据并保存为Excel"""
import os
import sys
import json
import requests

# 设置 SSO Token
SSO_TOKEN = 'BJ.CDD491446A1F26492FBCED004424D8AF.9520260626134502'
os.environ['SSO_TOKEN'] = SSO_TOKEN

BASE_URL = "http://da-api-99.jd.com/joy-claw-datasource/api/v1/datasourceAction"

def make_request(action, **params):
    """发送API请求"""
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"sso.jd.com={SSO_TOKEN}"
    }
    payload = {"action": action, **params}
    response = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

# Step 1: 获取数据源列表
print("=== 获取数据源列表 ===", flush=True)
try:
    result = make_request("GET_MY_DATASOURCE")
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
except Exception as e:
    print(f"获取数据源列表失败: {e}", flush=True)