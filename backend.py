import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RiskProfile:
    entity_id: str
    entity_type: str
    anomaly_score: float
    risk_level: str
    suspicion_indicators: List[str]
    behavioral_features: Dict[str, float]
    connected_entities: Dict[str, List[str]]
    created_at: str

class AnomalyDataExtractor:
    def __init__(self, data_dir: str = "data/gold/All_Beauty"):
        self.data_dir = Path(data_dir)
        self.anomaly_dir = self.data_dir / "anomaly_detection"
        self.hybrid_dir = self.data_dir / "hybrid_model"
        
        self._load_anomaly_data()
        self._load_graph_structure()
        self._load_hybrid_features()
    
    def _load_anomaly_data(self):
        self.anomaly_indices = np.load(self.anomaly_dir / "anomaly_indices.npy")
        self.hybrid_anomaly_scores = np.load(self.anomaly_dir / "hybrid_anomaly_scores.npy")
        self.graph_suspicion = np.load(self.anomaly_dir / "graph_suspicion.npy")
        self.semantic_suspicion = np.load(self.anomaly_dir / "semantic_suspicion.npy")
        self.pagerank_scores = np.load(self.anomaly_dir / "pagerank_scores.npy")
        
        with open(self.anomaly_dir / "anomaly_metadata.json", 'r') as f:
            self.anomaly_metadata = json.load(f)
            
    def _load_graph_structure(self):
        with open(self.hybrid_dir / "graph_structure.json", 'r') as f:
            self.graph_structure = json.load(f)
        with open(self.hybrid_dir / "id_mappings.json", 'r') as f:
            self.id_mappings = json.load(f)
            
    def _load_hybrid_features(self):
        self.combined_features = np.load(self.hybrid_dir / "combined_features.npy")
        self.labels = np.load(self.hybrid_dir / "labels.npy")
        self.splits = np.load(self.hybrid_dir / "splits.npy")
        with open(self.hybrid_dir / "metadata.json", 'r') as f:
            self.hybrid_metadata = json.load(f)
        # Load review nodes to create ID-to-index mapping
        self.reviews_df = pd.read_parquet(self.data_dir / "nodes_review.parquet")
        self.review_id_to_idx = {rid: idx for idx, rid in enumerate(self.reviews_df['review_id'])}
    
    def get_top_risky_reviews(self, n: int = 100, threshold: float = 0.7) -> List[Dict]:
        combined_risk = (
            0.4 * (self.hybrid_anomaly_scores / np.max(self.hybrid_anomaly_scores)) +
            0.3 * (self.graph_suspicion / np.max(self.graph_suspicion)) +
            0.3 * (self.semantic_suspicion / np.max(self.semantic_suspicion))
        )
        risky_indices = np.where(combined_risk > threshold)[0]
        risky_indices = risky_indices[np.argsort(combined_risk[risky_indices])[::-1]][:n]
        
        results = []
        for idx in risky_indices:
            results.append({
                'review_id': idx,
                'hybrid_anomaly_score': float(self.hybrid_anomaly_scores[idx]),
                'graph_suspicion': float(self.graph_suspicion[idx]),
                'semantic_suspicion': float(self.semantic_suspicion[idx]),
                'pagerank_score': float(self.pagerank_scores[idx]),
                'combined_risk_score': float(combined_risk[idx]),
                'label': int(self.labels[idx]),
                'split': int(self.splits[idx])
            })
        return results
    
    def get_risk_distribution(self) -> Dict[str, Any]:
        combined_risk = (
            0.4 * (self.hybrid_anomaly_scores / np.max(self.hybrid_anomaly_scores)) +
            0.3 * (self.graph_suspicion / np.max(self.graph_suspicion)) +
            0.3 * (self.semantic_suspicion / np.max(self.semantic_suspicion))
        )
        return {
            'low': int(np.sum(combined_risk < 0.3)),
            'medium': int(np.sum((combined_risk >= 0.3) & (combined_risk < 0.6))),
            'high': int(np.sum((combined_risk >= 0.6) & (combined_risk < 0.8))),
            'critical': int(np.sum(combined_risk >= 0.8)),
            'mean_score': float(np.mean(combined_risk)),
            'median_score': float(np.median(combined_risk)),
            'std_score': float(np.std(combined_risk))
        }

class GraphStructureAnalyzer:
    def __init__(self, extractor: AnomalyDataExtractor):
        self.extractor = extractor
        self._build_interaction_matrix()
        self._build_behavioral_pedigree()
    
    def _build_interaction_matrix(self):
        edges = self.extractor.graph_structure['edges_review_review']['edges']
        self.interaction_dict = defaultdict(list)
        for src, dst in edges:
            self.interaction_dict[src].append(dst)
            self.interaction_dict[dst].append(src)
            
    def _build_behavioral_pedigree(self):
        self.users_df = pd.read_parquet(self.extractor.data_dir / "nodes_user.parquet")
        self.reviews_df = pd.read_parquet(self.extractor.data_dir / "nodes_review.parquet")
        self.products_df = pd.read_parquet(self.extractor.data_dir / "nodes_item.parquet")
        self.user_review_edges = pd.read_parquet(self.extractor.data_dir / "edges_user_review.parquet")
        self.review_item_edges = pd.read_parquet(self.extractor.data_dir / "edges_review_item.parquet")
    
    def get_interaction_neighbors(self, review_id: int, depth: int = 2) -> Dict[str, Any]:
        neighbors = {'depth_0': [review_id], 'depth_1': [], 'depth_2': []}
        visited = {review_id}
        current_level = [review_id]
        
        for d in range(1, min(depth + 1, 3)):
            next_level = set()
            for node in current_level:
                for neighbor in self.interaction_dict.get(node, []):
                    if neighbor not in visited:
                        next_level.add(neighbor)
                        visited.add(neighbor)
            neighbors[f'depth_{d}'] = list(next_level)[:100]
            current_level = list(next_level)
        return neighbors
    
    def get_user_review_pedigree(self, user_id: str) -> Dict[str, Any]:
        try:
            user_reviews = self.user_review_edges[self.user_review_edges['src'] == user_id]
            review_data = []
            for _, row in user_reviews.iterrows():
                review_id = row['dst']
                review_idx = self.extractor.review_id_to_idx.get(review_id)
                if review_idx is not None and review_idx < len(self.extractor.labels):
                    # Get review details from reviews_df
                    review_row = self.extractor.reviews_df[self.extractor.reviews_df['review_id'] == review_id]
                    review_info = {
                        'review_id': review_id,
                        'label': int(self.extractor.labels[review_idx]),
                        'hybrid_anomaly_score': float(self.extractor.hybrid_anomaly_scores[review_idx]),
                        'graph_suspicion': float(self.extractor.graph_suspicion[review_idx]),
                        'rating': int(review_row['rating'].values[0]) if len(review_row) > 0 else 0,
                        'helpful_vote': int(review_row['helpful_vote'].values[0]) if len(review_row) > 0 else 0,
                        'verified_purchase': bool(review_row['verified_purchase'].values[0]) if len(review_row) > 0 else False,
                        'comment': str(review_row['text_clean'].values[0]) if len(review_row) > 0 and pd.notna(review_row['text_clean'].values[0]) else 'N/A'
                    }
                    review_data.append(review_info)
            return {
                'user_id': user_id,
                'num_reviews': len(review_data),
                'avg_anomaly_score': float(np.mean([r['hybrid_anomaly_score'] for r in review_data])) if review_data else 0,
                'avg_graph_suspicion': float(np.mean([r['graph_suspicion'] for r in review_data])) if review_data else 0,
                'reviews': review_data[:50]
            }
        except Exception as e:
            logger.error(f"Error in get_user_review_pedigree: {e}")
            return {'user_id': user_id, 'num_reviews': 0, 'reviews': []}
    
    def get_product_review_pedigree(self, product_id: str) -> Dict[str, Any]:
        try:
            product_reviews = self.review_item_edges[self.review_item_edges['dst'] == product_id]
            review_data = []
            for _, row in product_reviews.iterrows():
                review_id = row['src']
                review_idx = self.extractor.review_id_to_idx.get(review_id)
                if review_idx is not None and review_idx < len(self.extractor.labels):
                    # Get review details from reviews_df
                    review_row = self.extractor.reviews_df[self.extractor.reviews_df['review_id'] == review_id]
                    review_info = {
                        'review_id': review_id,
                        'user_id': str(review_row['user_id'].values[0]) if len(review_row) > 0 else 'N/A',
                        'label': int(self.extractor.labels[review_idx]),
                        'hybrid_anomaly_score': float(self.extractor.hybrid_anomaly_scores[review_idx]),
                        'semantic_suspicion': float(self.extractor.semantic_suspicion[review_idx]),
                        'rating': int(review_row['rating'].values[0]) if len(review_row) > 0 else 0,
                        'helpful_vote': int(review_row['helpful_vote'].values[0]) if len(review_row) > 0 else 0,
                        'verified_purchase': bool(review_row['verified_purchase'].values[0]) if len(review_row) > 0 else False,
                        'comment': str(review_row['text_clean'].values[0]) if len(review_row) > 0 and pd.notna(review_row['text_clean'].values[0]) else 'N/A'
                    }
                    review_data.append(review_info)
            return {
                'product_id': product_id,
                'num_reviews': len(review_data),
                'avg_anomaly_score': float(np.mean([r['hybrid_anomaly_score'] for r in review_data])) if review_data else 0,
                'risky_reviews': sum(1 for r in review_data if r['label'] == 1),
                'reviews': review_data[:50]
            }
        except Exception as e:
            logger.error(f"Error in get_product_review_pedigree: {e}")
            return {'product_id': product_id, 'num_reviews': 0, 'reviews': []}

class RiskAnalysisEngine:
    def __init__(self, data_dir: str = "data/gold/All_Beauty"):
        self.extractor = AnomalyDataExtractor(data_dir)
        self.graph_analyzer = GraphStructureAnalyzer(self.extractor)
    
    def query_by_review_id(self, review_id: int) -> Dict[str, Any]:
        if not (0 <= review_id < len(self.extractor.labels)):
            return {'error': f'Review ID {review_id} không hợp lệ'}
        
        neighbors = self.graph_analyzer.get_interaction_neighbors(review_id)
        return {
            'review_id': review_id,
            'risk_profile': {
                'hybrid_anomaly_score': float(self.extractor.hybrid_anomaly_scores[review_id]),
                'graph_suspicion': float(self.extractor.graph_suspicion[review_id]),
                'semantic_suspicion': float(self.extractor.semantic_suspicion[review_id]),
                'pagerank_score': float(self.extractor.pagerank_scores[review_id]),
                'label': int(self.extractor.labels[review_id]),
                'split': int(self.extractor.splits[review_id])
            },
            'behavioral_pedigree': neighbors,
            'interaction_count': len(self.graph_analyzer.interaction_dict.get(review_id, []))
        }
    
    def query_by_user_id(self, user_id: str) -> Dict[str, Any]:
        return self.graph_analyzer.get_user_review_pedigree(user_id)
    
    def query_by_product_id(self, product_id: str) -> Dict[str, Any]:
        return self.graph_analyzer.get_product_review_pedigree(product_id)
    
    def get_risk_log(self, top_n: int = 100, threshold: float = 0.7) -> List[Dict]:
        return self.extractor.get_top_risky_reviews(top_n, threshold)
    
    def get_system_statistics(self) -> Dict[str, Any]:
        return {
            'dataset_stats': {
                'num_users': self.extractor.hybrid_metadata['num_users'],
                'num_reviews': self.extractor.hybrid_metadata['num_reviews'],
                'num_items': self.extractor.hybrid_metadata['num_items'],
                'num_edges_review_review': self.extractor.hybrid_metadata['total_edges']
            },
            'risk_distribution': self.extractor.get_risk_distribution(),
            'timestamp': datetime.now().isoformat()
        }