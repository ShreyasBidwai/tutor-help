"""RAG (Retrieval-Augmented Generation) system for Niya Help Bot using TF-IDF"""
import os
import json
import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional

try:
    import faiss
except ImportError:
    faiss = None
    print("Warning: faiss-cpu not installed. RAG system will not work.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    print("Warning: scikit-learn not installed. RAG system will not work.")

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    print("Warning: google-generativeai not installed. RAG system will not work.")

class NiyaRAGSystem:
    """RAG system for Niya help bot using TF-IDF, FAISS and Gemini"""
    
    def __init__(self):
        self.vectorizer = None
        self.index = None
        self.qa_pairs = []
        self.embeddings = None
        self.similarity_threshold = 0.75
        self.faiss_index_path = 'data/niya_faiss.index'
        self.qa_data_path = 'data/niya_qa_pairs.json'
        self.embeddings_path = 'data/niya_embeddings.pkl'
        self.vectorizer_path = 'data/niya_vectorizer.pkl'
        
        # Initialize Gemini with fallback models
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key and genai is not None:
            try:
                genai.configure(api_key=api_key)
                # Model priority: gemini-2.5-flash (primary) -> gemini-2.5-flash-lite -> gemma-3-1b -> gemma-3-2b -> gemma-3-4b
                self.models = [
                    'gemini-2.5-flash',      # Primary: 5 RPM, 250K TPM, 20 RPD
                    'gemini-2.5-flash-lite', # Fallback 1: 10 RPM, 250K TPM, 20 RPD
                    'gemma-3-1b',            # Fallback 2: 30 RPM, 15K TPM, 14.4K RPD (smallest, fastest)
                    'gemma-3-2b',            # Fallback 3: 30 RPM, 15K TPM, 14.4K RPD
                    'gemma-3-4b',            # Fallback 4: 30 RPM, 15K TPM, 14.4K RPD
                ]
                self.current_model_index = 0
                self.gemini_model = genai.GenerativeModel(self.models[self.current_model_index])
                print(f"Initialized Gemini model: {self.models[self.current_model_index]}")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini: {e}")
                self.models = []
                self.current_model_index = 0
                self.gemini_model = None
        else:
            self.models = []
            self.current_model_index = 0
            self.gemini_model = None
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
    
    def load_vectorizer(self):
        """Load or create TF-IDF vectorizer"""
        if TfidfVectorizer is None:
            raise ImportError("scikit-learn is not installed. Install it with: pip install scikit-learn")
        
        if self.vectorizer is None:
            # Try to load existing vectorizer
            if os.path.exists(self.vectorizer_path):
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print("Loaded existing TF-IDF vectorizer")
            else:
                # Create new vectorizer
                self.vectorizer = TfidfVectorizer(
                    max_features=5000,  # Limit features for memory efficiency
                    stop_words='english',
                    ngram_range=(1, 2),  # Unigrams and bigrams
                    min_df=1,  # Minimum document frequency
                    max_df=0.95  # Maximum document frequency
                )
        return self.vectorizer
    
    def load_qa_pairs_from_json(self) -> List[Dict]:
        """Load Q&A pairs from JSON file"""
        if os.path.exists(self.qa_data_path):
            with open(self.qa_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create TF-IDF embeddings for a list of texts"""
        vectorizer = self.load_vectorizer()
        
        # Fit and transform (or just transform if already fitted)
        if not hasattr(vectorizer, 'vocabulary_') or len(vectorizer.vocabulary_) == 0:
            # First time - fit the vectorizer
            embeddings = vectorizer.fit_transform(texts)
        else:
            # Already fitted - just transform
            embeddings = vectorizer.transform(texts)
        
        # Convert to dense numpy array and normalize for cosine similarity
        embeddings_dense = embeddings.toarray().astype('float32')
        
        # Normalize for cosine similarity (L2 normalization)
        norms = np.linalg.norm(embeddings_dense, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        embeddings_dense = embeddings_dense / norms
        
        return embeddings_dense
    
    def build_faiss_index(self, qa_pairs: Optional[List[Dict]] = None, force_rebuild: bool = False):
        """Build or load FAISS index from Q&A pairs"""
        # Check if index already exists
        if not force_rebuild and os.path.exists(self.faiss_index_path) and os.path.exists(self.qa_data_path):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(self.faiss_index_path)
            with open(self.qa_data_path, 'r', encoding='utf-8') as f:
                self.qa_pairs = json.load(f)
            if os.path.exists(self.embeddings_path):
                with open(self.embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
            if os.path.exists(self.vectorizer_path):
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            print(f"Loaded {len(self.qa_pairs)} Q&A pairs from existing index")
            return
        
        # Load Q&A pairs if not provided
        if qa_pairs is None:
            qa_pairs = self.load_qa_pairs_from_json()
        
        if not qa_pairs:
            raise ValueError("No Q&A pairs found. Please create data/niya_qa_pairs.json first.")
        
        print("Building new FAISS index with TF-IDF...")
        self.qa_pairs = qa_pairs
        
        # Create TF-IDF embeddings for all questions
        questions = [qa['question'] for qa in qa_pairs]
        print(f"Creating TF-IDF embeddings for {len(questions)} questions...")
        self.embeddings = self.create_embeddings(questions)
        
        # Save vectorizer
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Create FAISS index
        if faiss is None:
            raise ImportError("faiss-cpu is not installed. Install it with: pip install faiss-cpu")
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity (already normalized)
        
        # Add embeddings to index
        self.index.add(self.embeddings)
        
        # Save index and data
        faiss.write_index(self.index, self.faiss_index_path)
        with open(self.qa_data_path, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
        
        print(f"FAISS index built and saved with {len(qa_pairs)} Q&A pairs")
    
    def search_similar(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Search for similar Q&A pairs using TF-IDF and cosine similarity"""
        if faiss is None:
            raise ImportError("faiss-cpu is not installed. Install it with: pip install faiss-cpu")
        if self.index is None or len(self.qa_pairs) == 0:
            return []
        
        # Create TF-IDF embedding for query
        vectorizer = self.load_vectorizer()
        query_embedding = vectorizer.transform([query])
        query_embedding_dense = query_embedding.toarray().astype('float32')
        
        # Normalize for cosine similarity
        norm = np.linalg.norm(query_embedding_dense)
        if norm > 0:
            query_embedding_dense = query_embedding_dense / norm
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding_dense, top_k)
        
        # Get results with similarity scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.qa_pairs) and idx >= 0:
                similarity = float(score)  # Cosine similarity (0-1)
                results.append((self.qa_pairs[idx], similarity))
        
        return results
    
    def get_rag_response(self, user_query: str, user_role: str = 'tutor', context: str = '') -> Dict:
        """Get response using RAG system with Gemini API"""
        # Search for similar Q&A pairs
        similar_results = self.search_similar(user_query, top_k=3)
        
        # Filter by similarity threshold
        high_similarity_results = [(qa, score) for qa, score in similar_results if score >= self.similarity_threshold]
        
        response_data = {
            'query': user_query,
            'similarity_scores': [score for _, score in similar_results],
            'used_rag': len(high_similarity_results) > 0,
            'response': ''
        }
        
        if high_similarity_results:
            # Use top 3 results for RAG
            top_results = high_similarity_results[:3]
            
            # Build context for Gemini
            context_text = "You are Niya, a cheerful and helpful assistant for TuitionTrack.\n\n"
            context_text += f"User role: {user_role}\n"
            if context:
                context_text += f"Context: {context}\n"
            context_text += "\nRelevant information from knowledge base:\n\n"
            
            for i, (qa, score) in enumerate(top_results, 1):
                context_text += f"{i}. Question: {qa['question']}\n"
                context_text += f"   Answer: {qa['answer']}\n\n"
            
            context_text += f"\nUser question: {user_query}\n\n"
            context_text += "Provide a helpful, cheerful response based on the information above. "
            context_text += "If the information doesn't fully answer the question, provide a general helpful response. "
            context_text += "Keep the response concise (2-4 sentences) and friendly."
            
            # Get response from Gemini with fallback
            if self.gemini_model and self.models:
                response_text = None
                last_error = None
                
                # Try current model and fallbacks
                for attempt in range(len(self.models)):
                    try:
                        model_name = self.models[self.current_model_index]
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(context_text)
                        response_text = response.text
                        response_data['rag_context'] = [qa['question'] for qa, _ in top_results]
                        response_data['model_used'] = model_name
                        break  # Success, exit loop
                    except Exception as e:
                        last_error = e
                        error_str = str(e).lower()
                        
                        # Check if it's a rate limit error
                        is_rate_limit = any(keyword in error_str for keyword in [
                            'rate limit', 'quota', '429', 'resource exhausted', 
                            'too many requests', 'per minute', 'per day'
                        ])
                        
                        if is_rate_limit and attempt < len(self.models) - 1:
                            # Try next model
                            self.current_model_index = (self.current_model_index + 1) % len(self.models)
                            print(f"Rate limit hit on {self.models[(self.current_model_index - 1) % len(self.models)]}, "
                                  f"switching to {self.models[self.current_model_index]}")
                            continue
                        else:
                            # Non-rate-limit error or last model, break
                            print(f"Error calling Gemini API ({self.models[self.current_model_index]}): {e}")
                            break
                
                if response_text:
                    response_data['response'] = response_text
                else:
                    # All models failed, use fallback answer
                    if top_results:
                        response_data['response'] = top_results[0][0]['answer']
                    else:
                        response_data['response'] = "I'm here to help! Could you please rephrase your question? 😊"
            else:
                # No Gemini API, use best match
                if top_results:
                    response_data['response'] = top_results[0][0]['answer']
                else:
                    response_data['response'] = "I'm here to help! Could you please rephrase your question? 😊"
        else:
            # Low similarity - ask for clarification or provide general response
            if self.gemini_model and self.models:
                response_text = None
                
                # Try current model and fallbacks
                for attempt in range(len(self.models)):
                    try:
                        model_name = self.models[self.current_model_index]
                        model = genai.GenerativeModel(model_name)
                        prompt = f"""You are Niya, a cheerful and helpful assistant for TuitionTrack.
User role: {user_role}
Context: {context}
User question: {user_query}

The user's question doesn't match any specific help topics. Provide a friendly, helpful response (2-3 sentences) that either:
1. Asks for clarification about what they need help with
2. Provides general guidance about TuitionTrack
3. Suggests they browse the help options

Keep it cheerful and helpful!"""
                        
                        response = model.generate_content(prompt)
                        response_text = response.text
                        response_data['model_used'] = model_name
                        break  # Success, exit loop
                    except Exception as e:
                        error_str = str(e).lower()
                        
                        # Check if it's a rate limit error
                        is_rate_limit = any(keyword in error_str for keyword in [
                            'rate limit', 'quota', '429', 'resource exhausted', 
                            'too many requests', 'per minute', 'per day'
                        ])
                        
                        if is_rate_limit and attempt < len(self.models) - 1:
                            # Try next model
                            self.current_model_index = (self.current_model_index + 1) % len(self.models)
                            print(f"Rate limit hit on {self.models[(self.current_model_index - 1) % len(self.models)]}, "
                                  f"switching to {self.models[self.current_model_index]}")
                            continue
                        else:
                            # Non-rate-limit error or last model
                            print(f"Error calling Gemini API ({self.models[self.current_model_index]}): {e}")
                            break
                
                if response_text:
                    response_data['response'] = response_text
                else:
                    response_data['response'] = "I'm here to help! Could you please rephrase your question? 😊"
            else:
                response_data['response'] = "I'm here to help! Could you please rephrase your question? 😊"
        
        return response_data

# Global RAG system instance
_rag_system = None

def get_rag_system() -> NiyaRAGSystem:
    """Get or create the global RAG system instance"""
    global _rag_system
    if _rag_system is None:
        _rag_system = NiyaRAGSystem()
    return _rag_system
