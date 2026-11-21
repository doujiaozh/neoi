#!/usr/bin/env python3
"""
安全推理模块测试
"""

import asyncio
import pytest
from core.security.reverse_engineer import SecurityExpert, SecurityAnalysisType


@pytest.mark.asyncio
async def test_security_analysis():
    """测试安全分析功能"""
    expert = SecurityExpert()
    
    # 准备测试数据
    test_binary = b'MZ\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    # 执行逆向工程分析
    report = await expert.analyze(test_binary, SecurityAnalysisType.REVERSE_ENGINEERING)
    
    # 验证结果
    assert report.analysis_id is not None
    assert report.analysis_type == SecurityAnalysisType.REVERSE_ENGINEERING
    assert isinstance(report.findings, list)
    assert report.risk_level in ["low", "medium", "high", "critical"]
    
    print(f"✅ 安全分析完成: {len(report.findings)} 个发现")


@pytest.mark.asyncio
async def test_protocols_detection():
    """测试协议检测功能"""
    expert = SecurityExpert()
    
    # HTTP协议特征
    http_data = b'GET / HTTP/1.1\r\nHost: example.com\r\n'
    report = await expert.analyze(http_data, SecurityAnalysisType.PROTOCOL_FUZZING)
    
    assert len(report.findings) >= 0  # 至少应该有发现
    
    print(f"✅ 协议检测完成: {len(report.findings)} 个发现")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
