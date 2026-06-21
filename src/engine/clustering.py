from typing import List, Dict
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from src.helpers.pydantic_models import MemoryFragment
import numpy as np

class ClusteringEngine:
    """
    Groups MemoryFragments into topical clusters.
    First segments by category, then uses TF-IDF and KMeans for semantic sub-clustering.
    """

    def __init__(self, n_clusters: int = 3):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def cluster(self, memories: List[MemoryFragment]) -> Dict[str, List[MemoryFragment]]:
        if not memories:
            return {}

        # 1. Segment by category - this is our "topical" clustering for now
        by_category = defaultdict(list)
        for mem in memories:
            by_category[mem.category].append(mem)

        return dict(by_category)
