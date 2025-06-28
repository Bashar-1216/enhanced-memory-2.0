export interface TextSegment {
  start: string
  end: string
  text: string
}

export interface Transcription {
  full_text: string
  segments: TextSegment[]
}

export interface Summaries {
  brief: string
  medium: string
  detailed: string
  key_points: string[]
}

export interface MultipleChoiceQuestion {
  question: string
  options: string[]
  correct_answer: number
  explanation: string
}

export interface OpenEndedQuestion {
  question: string
  key_points: string[]
}

export interface Questions {
  multiple_choice: MultipleChoiceQuestion[]
  open_ended: OpenEndedQuestion[]
}

export interface ConceptNode {
  id: string
  label: string
  type: string
  size: number
}

export interface ConceptEdge {
  from: string
  to: string
  label: string
  strength: number
}

export interface ConceptMap {
  nodes: ConceptNode[]
  edges: ConceptEdge[]
}

export interface SearchResult {
  segment: TextSegment
  score: number
  context: string
}

export interface LectureData {
  lecture_id: string
  title: string
  duration: string
  created_at: string
  transcription: Transcription
  summaries: Summaries
  questions: Questions
  concept_map: ConceptMap
  search_results: SearchResult[]
}
