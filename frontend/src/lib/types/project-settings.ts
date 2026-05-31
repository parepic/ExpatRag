export type ProjectSettings = {
  rag_strategy?: string | null;
  agent_type?: string | null;
  chunks_per_search?: number | null;
  final_context_size?: number | null;
  similarity_threshold?: number | null;
  number_of_queries?: number | null;
  vector_weight?: number | null;
  keyword_weight?: number | null;
};

export default ProjectSettings;
