"""NDOM Serializer — 序列化器 v0.2

支持 NDOM v0.2 对象的 JSON 序列化和反序列化。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from ndom.ndom import NDOM


class NDOMSerializer:
    """NDOM v0.2 序列化器。"""

    @staticmethod
    def to_json(ndom: NDOM, filepath: Optional[str] = None) -> str:
        """将 NDOM 实例序列化为 JSON 字符串。

        Args:
            ndom: NDOM 实例
            filepath: 可选的文件路径，若提供则写入文件

        Returns:
            JSON 字符串
        """
        data = ndom.to_dict()
        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    @staticmethod
    def from_json(json_str: str) -> Dict[str, Any]:
        """从 JSON 字符串解析为字典。"""
        return json.loads(json_str)

    @staticmethod
    def from_json_file(filepath: str) -> Dict[str, Any]:
        """从 JSON 文件解析。"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_object_sidecars(
        ndom: NDOM,
        output_dir: str,
    ) -> Dict[str, str]:
        """为每个 DataObject 保存独立侧车文件。

        Returns:
            文件路径映射 {object_id: path}
        """
        import os

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        paths = {}

        if ndom.dataset is None:
            return paths

        for obj in ndom.dataset.objects:
            obj_dir = output_path / obj.object_id[:8]
            obj_dir.mkdir(parents=True, exist_ok=True)

            # 安全侧车
            if obj.security_policy:
                fp = obj_dir / "security.json"
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(obj.security_policy.to_dict(), f, indent=2, ensure_ascii=False)

            # 风险画像侧车
            if obj.risk_profile:
                fp = obj_dir / "risk_profile.json"
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(obj.risk_profile.to_dict(), f, indent=2, ensure_ascii=False)

            # 指纹侧车
            if obj.fingerprint:
                fp = obj_dir / "fingerprint.json"
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(obj.fingerprint.to_dict(), f, indent=2, ensure_ascii=False)

            # 血缘侧车
            if obj.provenance:
                fp = obj_dir / "provenance.json"
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(obj.provenance.to_dict(), f, indent=2, ensure_ascii=False)

            # 访问元数据侧车
            if obj.access_metadata:
                fp = obj_dir / "access_metadata.json"
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(obj.access_metadata.to_dict(), f, indent=2, ensure_ascii=False)

            paths[obj.object_id] = str(obj_dir)

        return paths
