"""兼容旧命令：抓取文保单位完整镜像（网页、照片、保护范围图）。"""
from singdo_mirror import Archive

if __name__ == "__main__":
    Archive("wenbao", 6).run()
