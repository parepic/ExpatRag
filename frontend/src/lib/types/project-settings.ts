export type ProjectSettings = {
  rag_strategy: string;
  agent_type: string;
  chunks_per_search: number;
  final_context_size: number;
  similarity_threshold: number;
  number_of_queries?: number;
  vector_weight?: number;
  keyword_weight?: number;
};

export default ProjectSettings;
