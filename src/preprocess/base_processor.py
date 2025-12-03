from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """所有处理器的抽象基类，定义统一接口规范"""
    @abstractmethod
    def process(self, input_path: str, output_path: str, config: dict = None) -> None:
        """
        处理数据的核心方法，子类必须实现
        
        参数:
            input_path: 输入文件路径
            output_path: 输出文件路径
            config: 处理配置（可选）
        """
        pass