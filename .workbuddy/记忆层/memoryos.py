"""
MemoryOS 风格记忆系统
参考: BAI-LAB/MemoryOS (EMNLP 2025 Oral)

三层记忆架构:
- Short-term: 短期记忆 (FIFO淘汰)
- Mid-term: 中期记忆 (热度驱动)
- Long-term: 长期记忆 (知识沉淀)
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MemoryConfig:
    """MemoryOS 风格配置参数"""
    # 容量参数
    short_term_capacity: int = 7           # 短期记忆容量
    mid_term_capacity: int = 1000        # 中期记忆容量
    long_term_knowledge_capacity: int = 100  # 长期知识容量

    # 热度参数
    mid_term_heat_threshold: float = 5.0    # 中期热度阈值
    mid_term_similarity_threshold: float = 0.7  # 相似度阈值
    retrieval_queue_capacity: int = 7       # 检索队列容量

    # 衰减参数
    decay_factor: float = 0.95             # 热度衰减因子
    min_heat_to_keep: float = 1.0         # 最低保留热度


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    timestamp: str
    memory_type: str  # 'episodic' | 'semantic' | 'procedural' | 'emotional' | 'somatic'
    heat: float = 1.0  # 热度值
    access_count: int = 0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp,
            'memory_type': self.memory_type,
            'heat': self.heat,
            'access_count': self.access_count,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        return cls(**data)


class ShortTermMemory:
    """
    短期记忆 (Short-term Memory)
    - 容量: 7-10条
    - 淘汰: FIFO (先进先出)
    - 格式: JSONL (按天存储)
    """

    def __init__(self, storage_path: str, capacity: int = 7):
        self.storage_path = Path(storage_path) / 'short_term'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.capacity = capacity
        self._memory: List[MemoryEntry] = []
        self._load_today()

    def _get_today_file(self) -> Path:
        return self.storage_path / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"

    def _load_today(self):
        """加载今天的记忆"""
        today_file = self._get_today_file()
        if today_file.exists():
            with open(today_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self._memory.append(MemoryEntry.from_dict(json.loads(line)))

    def add(self, entry: MemoryEntry) -> List[MemoryEntry]:
        """
        添加记忆，返回被淘汰的记忆（需要晋升到中期）
        """
        self._memory.append(entry)
        self._save(entry)

        # FIFO 淘汰
        evicted = []
        while len(self._memory) > self.capacity:
            old_entry = self._memory.pop(0)
            evicted.append(old_entry)

        return evicted

    def _save(self, entry: MemoryEntry):
        """持久化到文件"""
        today_file = self._get_today_file()
        with open(today_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')

    def get_all(self) -> List[MemoryEntry]:
        return self._memory.copy()

    def get_recent(self, n: int = 5) -> List[MemoryEntry]:
        return self._memory[-n:]


class MidTermMemory:
    """
    中期记忆 (Mid-term Memory)
    - 容量: 1000条
    - 热度驱动晋升到长期
    - 相似度合并
    """

    def __init__(self, storage_path: str, capacity: int = 1000,
                 heat_threshold: float = 5.0, similarity_threshold: float = 0.7):
        self.storage_path = Path(storage_path) / 'mid_term'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.capacity = capacity
        self.heat_threshold = heat_threshold
        self.similarity_threshold = similarity_threshold
        self._memory: List[MemoryEntry] = []
        self._load_all()

    def _load_all(self):
        """加载所有中期记忆"""
        for file in self.storage_path.glob('*.json'):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        self._memory.append(MemoryEntry.from_dict(item))

    def _save_all(self):
        """持久化所有中期记忆"""
        # 按类型分组存储
        by_type = {}
        for entry in self._memory:
            if entry.memory_type not in by_type:
                by_type[entry.memory_type] = []
            by_type[entry.memory_type].append(entry.to_dict())

        for mem_type, entries in by_type.items():
            file_path = self.storage_path / f"{mem_type}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)

    def add(self, entry: MemoryEntry) -> Tuple[List[MemoryEntry], Optional[MemoryEntry]]:
        """
        添加记忆，返回:
        - 需要晋升到长期记忆的条目
        - 被淘汰的条目（容量超限）
        """
        # 检查相似度，合并相近记忆
        merged = self._maybe_merge(entry)
        if merged:
            return [], None

        self._memory.append(entry)

        # 检查是否需要晋升
        promoted = []
        evicted = []

        # 热度超过阈值 → 晋升到长期
        if entry.heat >= self.heat_threshold:
            promoted.append(entry)
            self._memory.remove(entry)

        # 容量超限 → 淘汰低热度
        while len(self._memory) > self.capacity:
            # 找最低热度的条目
            min_heat_entry = min(self._memory, key=lambda x: x.heat)
            self._memory.remove(min_heat_entry)
            evicted.append(min_heat_entry)

        self._save_all()
        return promoted, evicted

    def _maybe_merge(self, new_entry: MemoryEntry) -> bool:
        """检查相似度，合并相近记忆"""
        for existing in self._memory:
            if existing.memory_type == new_entry.memory_type:
                # 词级 Jaccard 相似度判断
                new_words = set(new_entry.content.split())
                existing_words = set(existing.content.split())
                if not new_words:
                    continue
                overlap = len(new_words & existing_words)
                if overlap > len(new_words) * self.similarity_threshold:
                    # 合并内容，更新热度
                    existing.content += f"\n{new_entry.content}"
                    existing.heat = max(existing.heat, new_entry.heat)
                    existing.access_count += new_entry.access_count
                    return True
        return False

    def access(self, entry_id: str) -> Optional[MemoryEntry]:
        """访问记忆，增加热度"""
        for entry in self._memory:
            if entry.id == entry_id:
                entry.access_count += 1
                entry.heat = entry.heat * 0.95 + 1.0  # 热度计算
                return entry
        return None

    def get_by_type(self, mem_type: str) -> List[MemoryEntry]:
        return [e for e in self._memory if e.memory_type == mem_type]


class LongTermMemory:
    """
    长期记忆 (Long-term Memory)
    - 容量: 100条
    - 存储: 用户画像、知识库、策略
    - 持久化: JSON files (user_profile / knowledge / strategies)
    """

    def __init__(self, storage_path: str, capacity: int = 100):
        self.storage_path = Path(storage_path) / 'long_term'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.capacity = capacity

        # 子目录
        self.user_profile_path = self.storage_path / 'user_profile'
        self.knowledge_path = self.storage_path / 'knowledge'
        self.strategies_path = self.storage_path / 'strategies'

        for path in [self.user_profile_path, self.knowledge_path, self.strategies_path]:
            path.mkdir(parents=True, exist_ok=True)

        self._load_all()

    def _load_all(self):
        """加载所有长期记忆"""
        self.user_profile = self._load_json(self.user_profile_path / 'profile.json', {
            'name': '',
            'preferences': {},
            'work_style': {},
            'interactions': 0
        })
        self.knowledge = self._load_list(self.knowledge_path)
        self.strategies = self._load_list(self.strategies_path)

    def _load_json(self, path: Path, default: dict) -> dict:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default

    def _load_list(self, path: Path) -> List[Dict]:
        items = []
        for file in path.glob('*.json'):
            with open(file, 'r', encoding='utf-8') as f:
                items.append(json.load(f))
        return items

    def update_user_profile(self, updates: Dict):
        """更新用户画像"""
        self.user_profile.update(updates)
        self.user_profile['updated_at'] = datetime.now().isoformat()

        profile_file = self.user_profile_path / 'profile.json'
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_profile, f, ensure_ascii=False, indent=2)

    def add_knowledge(self, knowledge: Dict) -> bool:
        """添加知识"""
        if len(self.knowledge) >= self.capacity:
            # 删除最旧的知识
            self.knowledge.pop(0)

        knowledge['added_at'] = datetime.now().isoformat()
        self.knowledge.append(knowledge)

        # 保存到文件
        safe_name = knowledge.get('id', f"kg_{len(self.knowledge)}")
        file_path = self.knowledge_path / f"{safe_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)

        return True

    def add_strategy(self, strategy: Dict) -> bool:
        """添加策略"""
        if len(self.strategies) >= self.capacity // 2:
            self.strategies.pop(0)

        strategy['added_at'] = datetime.now().isoformat()
        self.strategies.append(strategy)

        safe_name = strategy.get('id', f"str_{len(self.strategies)}")
        file_path = self.strategies_path / f"{safe_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)

        return True

    def get_context(self, query: str = None) -> Dict:
        """获取上下文（用于生成响应）"""
        return {
            'user_profile': self.user_profile,
            'recent_knowledge': self.knowledge[-10:],
            'strategies': self.strategies
        }


class MemoryOS:
    """
    MemoryOS 风格记忆系统主类
    整合三层记忆 + 五种记忆类型
    """

    def __init__(self, storage_path: str, config: MemoryConfig = None):
        self.config = config or MemoryConfig()
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 初始化三层记忆
        self.short_term = ShortTermMemory(
            str(self.storage_path),
            self.config.short_term_capacity
        )
        self.mid_term = MidTermMemory(
            str(self.storage_path),
            self.config.mid_term_capacity,
            self.config.mid_term_heat_threshold,
            self.config.mid_term_similarity_threshold
        )
        self.long_term = LongTermMemory(
            str(self.storage_path),
            self.config.long_term_knowledge_capacity
        )

    def add_memory(self, content: str, memory_type: str = 'episodic',
                   metadata: Dict = None) -> Dict:
        """
        添加记忆，自动处理层级晋升
        返回: 记忆处理结果
        """
        import uuid
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.now().isoformat(),
            memory_type=memory_type,
            heat=1.0,
            metadata=metadata or {}
        )

        # 1. 先添加到短期记忆
        evicted = self.short_term.add(entry)

        # 2. 处理从短期晋升的条目
        promoted_to_long = []
        for ev_entry in evicted:
            promoted, _ = self.mid_term.add(ev_entry)
            promoted_to_long.extend(promoted)

        # 3. 处理从中级晋升的条目
        for long_entry in promoted_to_long:
            if long_entry.memory_type == 'emotional':
                # 情感记忆 → 更新用户画像
                self.long_term.update_user_profile(long_entry.metadata)
            elif long_entry.memory_type == 'semantic':
                # 语义记忆 → 添加到知识库
                self.long_term.add_knowledge({
                    'id': long_entry.id,
                    'content': long_entry.content,
                    'metadata': long_entry.metadata
                })
            elif long_entry.memory_type == 'procedural':
                # 程序记忆 → 添加策略
                self.long_term.add_strategy({
                    'id': long_entry.id,
                    'content': long_entry.content,
                    'metadata': long_entry.metadata
                })

        return {
            'status': 'added',
            'entry_id': entry.id,
            'current_short_term_count': len(self.short_term.get_all()),
            'promoted_to_long': len(promoted_to_long)
        }

    def retrieve(self, query: str, memory_types: List[str] = None) -> Dict:
        """
        检索记忆
        返回: 来自三层记忆的检索结果
        """
        if memory_types is None:
            memory_types = ['episodic', 'semantic', 'procedural', 'emotional']

        results = {
            'short_term': [],
            'mid_term': [],
            'long_term': [],
            'context': {}
        }

        # 短期记忆
        for entry in self.short_term.get_all():
            if entry.memory_type in memory_types:
                results['short_term'].append(entry.to_dict())

        # 中期记忆
        for mem_type in memory_types:
            for entry in self.mid_term.get_by_type(mem_type):
                # 增加热度
                self.mid_term.access(entry.id)
                results['mid_term'].append(entry.to_dict())

        # 长期记忆上下文
        results['context'] = self.long_term.get_context(query)

        return results

    def get_memory_summary(self) -> Dict:
        """获取记忆系统状态"""
        return {
            'short_term_count': len(self.short_term.get_all()),
            'mid_term_count': len(self.mid_term._memory),
            'long_term_knowledge': len(self.long_term.knowledge),
            'long_term_strategies': len(self.long_term.strategies),
            'user_profile': self.long_term.user_profile.get('name', 'Unknown'),
            'config': {
                'short_term_capacity': self.config.short_term_capacity,
                'mid_term_capacity': self.config.mid_term_capacity,
                'heat_threshold': self.config.mid_term_heat_threshold
            }

        }

    def search_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """在所有三层记忆中搜索"""
        results = []
        seen_ids = set()
        query_lower = query.lower()

        for entry in self.short_term.get_all():
            if query_lower in entry.content.lower() and entry.id not in seen_ids:
                seen_ids.add(entry.id)
                results.append({"layer": "short_term", "content": entry.content[:200], "time": entry.timestamp, "score": 1.0, "memory_type": entry.memory_type})

        for mem_type in ['episodic', 'semantic', 'procedural', 'emotional']:
            for entry in self.mid_term.get_by_type(mem_type):
                if query_lower in entry.content.lower() and entry.id not in seen_ids:
                    seen_ids.add(entry.id)
                    self.mid_term.access(entry.id)
                    results.append({"layer": "mid_term", "content": entry.content[:200], "time": entry.timestamp, "score": min(entry.heat / 5.0, 1.0), "memory_type": entry.memory_type})

        for item in self.long_term.knowledge:
            content = item.get("content", "")
            item_id = item.get("id", content[:20])
            if query_lower in content.lower() and item_id not in seen_ids:
                seen_ids.add(item_id)
                results.append({"layer": "long_term", "content": content[:200], "time": item.get("added_at", ""), "score": 0.8, "memory_type": "semantic"})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def save_checkpoint(self):
        """持久化所有层"""
        self.mid_term._save_all()
        st_count = len(self.short_term.get_all())
        mt_count = len(self.mid_term._memory)
        lt_count = len(self.long_term.knowledge)
        print(f"[MemoryOS] Checkpoint saved — ST:{st_count} MT:{mt_count} LT:{lt_count}")


# ============ 使用示例 ============

if __name__ == '__main__':
    # 初始化
    memory = MemoryOS(
        storage_path='./memory_data',
        config=MemoryConfig(
            short_term_capacity=7,
            mid_term_capacity=100,
            mid_term_heat_threshold=5.0
        )
    )

    # 添加记忆
    print("=== 添加记忆 ===")
    memory.add_memory(
        content="用户偏好简洁直接的回复风格",
        memory_type='emotional',
        metadata={'category': 'communication_style'}
    )

    memory.add_memory(
        content="三层架构 = raw + processed + knowledge + vector + api",
        memory_type='semantic',
        metadata={'concept': 'architecture'}
    )

    memory.add_memory(
        content="做事顺序 = 先求有 + 再求丰富 + 再求杂 + 提炼精华 + 延伸重构",
        memory_type='procedural',
        metadata={'pattern': '做事方法'}
    )

    # 检索
    print("\n=== 检索记忆 ===")
    results = memory.retrieve("架构")
    print(f"找到 {len(results['short_term'])} 条短期记忆")
    print(f"找到 {len(results['mid_term'])} 条中期记忆")

    # 状态
    print("\n=== 记忆系统状态 ===")
    summary = memory.get_memory_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
