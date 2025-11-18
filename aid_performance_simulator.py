#!/usr/bin/env python3
"""
AiD Performance Simulator and Analyzer
Analyzes startup logs and runtime performance metrics
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class SystemModule:
    """Represents a system module with initialization status"""
    name: str
    status: str  # OK, FAILED, WARNING, MISSING
    init_time: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class MemoryMetrics:
    """Memory system performance metrics"""
    stm_messages: int = 0
    runtime_messages: int = 0
    ltm_memories: int = 0
    retrieval_count: int = 0
    avg_retrieval_score: float = 0.0
    auto_save_active: bool = False


@dataclass
class RAGMetrics:
    """RAG database performance metrics"""
    total_datasets: int = 0
    total_vectors: int = 0
    datasets: Dict[str, int] = field(default_factory=dict)
    load_time: float = 0.0
    embedding_model_loaded: bool = False


@dataclass
class VoiceMetrics:
    """Voice system performance metrics"""
    tts_initialized: bool = False
    stt_initialized: bool = False
    reference_samples: int = 0
    tts_processing_time: List[float] = field(default_factory=list)
    real_time_factor: List[float] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)


@dataclass
class ConversationMetrics:
    """Conversation processing metrics"""
    total_calls: int = 0
    avg_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    mode_distribution: Dict[str, int] = field(default_factory=dict)
    token_usage: List[Dict[str, int]] = field(default_factory=list)
    emotions_detected: Dict[str, int] = field(default_factory=dict)


@dataclass
class RelationshipMetrics:
    """Relationship tracking metrics"""
    stage: str = "unknown"
    days: int = 0
    exchanges: int = 0
    intimacy: int = 0
    progression_rate: float = 0.0


@dataclass
class PerformanceReport:
    """Complete performance analysis report"""
    startup_success: bool = False
    startup_warnings: List[str] = field(default_factory=list)
    startup_errors: List[str] = field(default_factory=list)
    modules: Dict[str, SystemModule] = field(default_factory=dict)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    rag: RAGMetrics = field(default_factory=RAGMetrics)
    voice: VoiceMetrics = field(default_factory=VoiceMetrics)
    conversation: ConversationMetrics = field(default_factory=ConversationMetrics)
    relationship: RelationshipMetrics = field(default_factory=RelationshipMetrics)
    overall_health_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


class AiDPerformanceSimulator:
    """Simulates and analyzes AiD system performance from logs"""

    def __init__(self):
        self.report = PerformanceReport()
        self.current_timestamp = None

    def parse_logs(self, log_text: str) -> PerformanceReport:
        """Parse log text and generate performance report"""
        lines = log_text.strip().split('\n')

        for line in lines:
            self._process_log_line(line)

        # Calculate derived metrics
        self._calculate_health_score()
        self._generate_recommendations()

        return self.report

    def _process_log_line(self, line: str):
        """Process a single log line"""
        # Extract timestamp if present
        timestamp_match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
        if timestamp_match:
            self.current_timestamp = timestamp_match.group(1)

        # Startup module initialization
        if '[STARTUP]' in line:
            if 'Performing system checks' in line:
                self.report.modules['startup'] = SystemModule('startup', 'OK')
            elif 'fully ready and online' in line:
                self.report.startup_success = True
            elif '✗' in line or 'ERROR' in line.upper():
                error_msg = line.split('✗')[-1].strip() if '✗' in line else line
                self.report.startup_errors.append(error_msg)

        # Memory system
        elif '[MEMORY_INIT]' in line or '[MEMORY]' in line or '[STM]' in line:
            self._process_memory_line(line)

        # RAG system
        elif '[RAG]' in line:
            self._process_rag_line(line)

        # Voice system
        elif '[VOICE' in line:
            self._process_voice_line(line)

        # Persona and advanced systems
        elif '[PERSONA]' in line or '[ADVANCED]' in line:
            self._process_persona_line(line)

        # Relationship tracking
        elif '[RELATIONSHIP]' in line:
            self._process_relationship_line(line)

        # Conversation calls
        elif '[CALL #' in line:
            self._process_conversation_call(line)

        # Response info
        elif '[INFO]' in line and 'Response in' in line:
            self._process_response_info(line)

        # Emotion detection
        elif '[EMOTION]' in line and 'Detected:' in line:
            self._process_emotion_line(line)

        # Token breakdown
        elif '[TOKENS]' in line or 'Breakdown:' in line:
            self._process_token_line(line)

        # Warnings
        elif '⚠️' in line or 'WARNING' in line.upper():
            warning_msg = line.split('⚠️')[-1].strip() if '⚠️' in line else line
            self.report.startup_warnings.append(warning_msg)

        # Auto-response warnings
        elif '[Auto-Response Startup Warnings]' in line:
            pass  # Section header
        elif 'Module missing:' in line:
            missing_module = line.split('Module missing:')[-1].strip()
            self.report.startup_warnings.append(f"Missing module: {missing_module}")

    def _process_memory_line(self, line: str):
        """Process memory-related log lines"""
        if 'Loaded' in line and 'messages from STM' in line:
            match = re.search(r'Loaded (\d+) messages from STM', line)
            if match:
                self.report.memory.stm_messages = int(match.group(1))

        elif 'Runtime buffer size:' in line or 'Buffer size:' in line:
            match = re.search(r'(\d+) messages', line)
            if match:
                self.report.memory.runtime_messages = int(match.group(1))

        elif 'Auto-save enabled' in line or 'Auto-save loop started' in line:
            self.report.memory.auto_save_active = True

        elif 'Loaded' in line and 'memories from disk' in line:
            match = re.search(r'Loaded (\d+) memories', line)
            if match:
                self.report.memory.ltm_memories = int(match.group(1))

        elif 'Found' in line and 'high-quality memories' in line:
            match = re.search(r'Found (\d+) high-quality', line)
            if match:
                self.report.memory.retrieval_count = int(match.group(1))

    def _process_rag_line(self, line: str):
        """Process RAG-related log lines"""
        if "Loaded '" in line and "' with" in line and "vectors" in line:
            match = re.search(r"Loaded '(\w+)' with (\d+) vectors", line)
            if match:
                dataset_name = match.group(1)
                vector_count = int(match.group(2))
                self.report.rag.datasets[dataset_name] = vector_count
                self.report.rag.total_vectors += vector_count
                self.report.rag.total_datasets += 1

        elif 'All indexes loaded:' in line:
            match = re.search(r'(\d+) datasets, (\d+) total vectors', line)
            if match:
                self.report.rag.total_datasets = int(match.group(1))
                self.report.rag.total_vectors = int(match.group(2))

        elif 'Embedding model loaded' in line:
            self.report.rag.embedding_model_loaded = True

    def _process_voice_line(self, line: str):
        """Process voice-related log lines"""
        if 'TTS initialized' in line:
            self.report.voice.tts_initialized = True

        elif 'STT initialized' in line:
            self.report.voice.stt_initialized = True

        elif 'Found' in line and 'reference samples' in line:
            match = re.search(r'Found (\d+) reference samples', line)
            if match:
                self.report.voice.reference_samples = int(match.group(1))

        elif 'Processing time:' in line:
            match = re.search(r'Processing time: ([\d.]+)', line)
            if match:
                self.report.voice.tts_processing_time.append(float(match.group(1)))

        elif 'Real-time factor:' in line:
            match = re.search(r'Real-time factor: ([\d.]+)', line)
            if match:
                self.report.voice.real_time_factor.append(float(match.group(1)))

        elif 'Failed to initialize' in line or 'VOICE]' in line and 'Failed' in line:
            self.report.voice.failures.append(line.strip())

    def _process_persona_line(self, line: str):
        """Process persona and advanced system lines"""
        if '✓' in line or '✔' in line or '[OK]' in line:
            # Extract module name
            for keyword in ['Personality loaded', 'Relationship tracking', 'Proactive engagement',
                           'Emotional intelligence', 'Preference learning', 'Conversation intelligence',
                           'Routine learning', 'Topic threading', 'Socratic mode', 'Context layering',
                           'Vulnerability matching', 'Strategic silence', 'Disagreement engine']:
                if keyword.lower() in line.lower():
                    module_name = keyword.lower().replace(' ', '_')
                    self.report.modules[module_name] = SystemModule(module_name, 'OK')

    def _process_relationship_line(self, line: str):
        """Process relationship tracking lines"""
        if 'Stage:' in line:
            match = re.search(r'Stage: (\w+)', line)
            if match:
                self.report.relationship.stage = match.group(1)

        if 'Days:' in line:
            match = re.search(r'Days: (\d+)', line)
            if match:
                self.report.relationship.days = int(match.group(1))

        if 'Exchanges:' in line:
            match = re.search(r'Exchanges: (\d+)', line)
            if match:
                self.report.relationship.exchanges = int(match.group(1))

        if 'Intimacy:' in line:
            match = re.search(r'Intimacy: (\d+)/100', line)
            if match:
                self.report.relationship.intimacy = int(match.group(1))

    def _process_conversation_call(self, line: str):
        """Process conversation call lines"""
        match = re.search(r'\[CALL #(\d+)\]', line)
        if match:
            self.report.conversation.total_calls += 1

    def _process_response_info(self, line: str):
        """Process response info lines"""
        # Extract response time
        match = re.search(r'Response in ([\d.]+)s', line)
        if match:
            response_time = float(match.group(1))
            self.report.conversation.response_times.append(response_time)

        # Extract mode
        match = re.search(r'Mode: (\w+)', line)
        if match:
            mode = match.group(1)
            self.report.conversation.mode_distribution[mode] = \
                self.report.conversation.mode_distribution.get(mode, 0) + 1

    def _process_emotion_line(self, line: str):
        """Process emotion detection lines"""
        match = re.search(r'Detected: (\w+)', line)
        if match:
            emotion = match.group(1)
            self.report.conversation.emotions_detected[emotion] = \
                self.report.conversation.emotions_detected.get(emotion, 0) + 1

    def _process_token_line(self, line: str):
        """Process token usage lines"""
        # This would extract token breakdown
        # Implementation depends on specific token format in logs
        pass

    def _calculate_health_score(self):
        """Calculate overall system health score (0-100)"""
        score = 100.0

        # Deduct for startup errors
        score -= len(self.report.startup_errors) * 10

        # Deduct for startup warnings
        score -= len(self.report.startup_warnings) * 2

        # Deduct if not fully started
        if not self.report.startup_success:
            score -= 20

        # Deduct for voice failures
        score -= len(self.report.voice.failures) * 5

        # Deduct for missing critical modules
        critical_modules = ['memory_system', 'rag_system', 'persona_system']
        for module in critical_modules:
            if module not in self.report.modules or self.report.modules[module].status != 'OK':
                score -= 10

        # Bonus for successful initializations
        if self.report.memory.auto_save_active:
            score += 5
        if self.report.rag.embedding_model_loaded:
            score += 5
        if self.report.voice.tts_initialized:
            score += 5

        # Cap at 0-100
        self.report.overall_health_score = max(0.0, min(100.0, score))

    def _generate_recommendations(self):
        """Generate performance recommendations"""
        recommendations = []

        # Memory warnings
        if not self.report.memory.auto_save_active:
            recommendations.append("⚠️ Memory auto-save is not active. Data may be lost.")

        # Missing modules
        if self.report.startup_warnings:
            for warning in self.report.startup_warnings:
                if 'Module missing' in warning:
                    recommendations.append(f"🔧 {warning} - Consider implementing this module.")

        # Voice performance
        if self.report.voice.tts_processing_time:
            avg_tts_time = sum(self.report.voice.tts_processing_time) / len(self.report.voice.tts_processing_time)
            if avg_tts_time > 30:
                recommendations.append(f"⚡ TTS processing is slow (avg {avg_tts_time:.2f}s). Consider GPU acceleration.")

        if self.report.voice.real_time_factor:
            avg_rtf = sum(self.report.voice.real_time_factor) / len(self.report.voice.real_time_factor)
            if avg_rtf > 2.0:
                recommendations.append(f"⚡ Real-time factor is high ({avg_rtf:.2f}x). Voice output is slower than real-time.")

        # Voice failures
        if self.report.voice.failures:
            recommendations.append(f"❌ Voice system has {len(self.report.voice.failures)} failures. Check voice handler initialization.")

        # Response time
        if self.report.conversation.response_times:
            avg_response = sum(self.report.conversation.response_times) / len(self.report.conversation.response_times)
            if avg_response > 5.0:
                recommendations.append(f"⚡ Average response time is {avg_response:.2f}s. Consider optimizing memory retrieval.")

        # RAG performance
        if self.report.rag.total_vectors > 1000000:
            recommendations.append(f"💾 RAG database is large ({self.report.rag.total_vectors:,} vectors). Consider index optimization.")

        # Relationship progression
        if self.report.relationship.intimacy > 0:
            progression_rate = self.report.relationship.intimacy / max(1, self.report.relationship.days)
            if progression_rate < 1.5:
                recommendations.append(f"💬 Intimacy progression is slow ({progression_rate:.2f} points/day). Enhance interaction depth.")

        # Success indicators
        if self.report.overall_health_score >= 90:
            recommendations.append("✅ System is performing excellently!")
        elif self.report.overall_health_score >= 75:
            recommendations.append("✓ System is performing well with minor issues.")
        elif self.report.overall_health_score >= 50:
            recommendations.append("⚠️ System has moderate issues that should be addressed.")
        else:
            recommendations.append("❌ System has critical issues requiring immediate attention.")

        self.report.recommendations = recommendations

    def generate_report_text(self) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("=" * 80)
        lines.append("AiD PERFORMANCE SIMULATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Overall Health
        lines.append(f"OVERALL HEALTH SCORE: {self.report.overall_health_score:.1f}/100")
        lines.append("")

        # Startup Status
        lines.append("STARTUP STATUS")
        lines.append("-" * 80)
        lines.append(f"  Startup Success: {'✅ YES' if self.report.startup_success else '❌ NO'}")
        lines.append(f"  Errors: {len(self.report.startup_errors)}")
        for error in self.report.startup_errors:
            lines.append(f"    ❌ {error}")
        lines.append(f"  Warnings: {len(self.report.startup_warnings)}")
        for warning in self.report.startup_warnings[:5]:  # Show first 5
            lines.append(f"    ⚠️ {warning}")
        if len(self.report.startup_warnings) > 5:
            lines.append(f"    ... and {len(self.report.startup_warnings) - 5} more")
        lines.append("")

        # Module Status
        lines.append("MODULE STATUS")
        lines.append("-" * 80)
        for module_name, module in self.report.modules.items():
            status_icon = "✅" if module.status == "OK" else "❌"
            lines.append(f"  {status_icon} {module_name}: {module.status}")
        lines.append("")

        # Memory System
        lines.append("MEMORY SYSTEM PERFORMANCE")
        lines.append("-" * 80)
        lines.append(f"  STM Messages: {self.report.memory.stm_messages}")
        lines.append(f"  Runtime Messages: {self.report.memory.runtime_messages}")
        lines.append(f"  LTM Memories: {self.report.memory.ltm_memories}")
        lines.append(f"  Memory Retrieval Count: {self.report.memory.retrieval_count}")
        lines.append(f"  Auto-Save Active: {'✅ YES' if self.report.memory.auto_save_active else '❌ NO'}")
        lines.append("")

        # RAG System
        lines.append("RAG DATABASE PERFORMANCE")
        lines.append("-" * 80)
        lines.append(f"  Total Datasets: {self.report.rag.total_datasets}")
        lines.append(f"  Total Vectors: {self.report.rag.total_vectors:,}")
        lines.append(f"  Embedding Model Loaded: {'✅ YES' if self.report.rag.embedding_model_loaded else '❌ NO'}")
        lines.append("  Dataset Breakdown:")
        for dataset, count in sorted(self.report.rag.datasets.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.report.rag.total_vectors * 100) if self.report.rag.total_vectors > 0 else 0
            lines.append(f"    • {dataset}: {count:,} vectors ({percentage:.1f}%)")
        lines.append("")

        # Voice System
        lines.append("VOICE SYSTEM PERFORMANCE")
        lines.append("-" * 80)
        lines.append(f"  TTS Initialized: {'✅ YES' if self.report.voice.tts_initialized else '❌ NO'}")
        lines.append(f"  STT Initialized: {'✅ YES' if self.report.voice.stt_initialized else '❌ NO'}")
        lines.append(f"  Reference Samples: {self.report.voice.reference_samples}")
        if self.report.voice.tts_processing_time:
            avg_tts = sum(self.report.voice.tts_processing_time) / len(self.report.voice.tts_processing_time)
            min_tts = min(self.report.voice.tts_processing_time)
            max_tts = max(self.report.voice.tts_processing_time)
            lines.append(f"  TTS Processing Time: avg={avg_tts:.2f}s, min={min_tts:.2f}s, max={max_tts:.2f}s")
        if self.report.voice.real_time_factor:
            avg_rtf = sum(self.report.voice.real_time_factor) / len(self.report.voice.real_time_factor)
            lines.append(f"  Real-Time Factor: {avg_rtf:.2f}x (lower is better, <1.0 is real-time)")
        lines.append(f"  Failures: {len(self.report.voice.failures)}")
        for failure in self.report.voice.failures[:3]:
            lines.append(f"    ❌ {failure}")
        lines.append("")

        # Conversation Performance
        lines.append("CONVERSATION PERFORMANCE")
        lines.append("-" * 80)
        lines.append(f"  Total API Calls: {self.report.conversation.total_calls}")
        if self.report.conversation.response_times:
            avg_resp = sum(self.report.conversation.response_times) / len(self.report.conversation.response_times)
            min_resp = min(self.report.conversation.response_times)
            max_resp = max(self.report.conversation.response_times)
            lines.append(f"  Response Time: avg={avg_resp:.2f}s, min={min_resp:.2f}s, max={max_resp:.2f}s")
        if self.report.conversation.mode_distribution:
            lines.append("  Mode Distribution:")
            for mode, count in sorted(self.report.conversation.mode_distribution.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"    • {mode}: {count} calls")
        if self.report.conversation.emotions_detected:
            lines.append("  Emotions Detected:")
            for emotion, count in sorted(self.report.conversation.emotions_detected.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"    • {emotion}: {count} times")
        lines.append("")

        # Relationship Metrics
        lines.append("RELATIONSHIP TRACKING")
        lines.append("-" * 80)
        lines.append(f"  Current Stage: {self.report.relationship.stage.upper()}")
        lines.append(f"  Days Active: {self.report.relationship.days}")
        lines.append(f"  Total Exchanges: {self.report.relationship.exchanges}")
        lines.append(f"  Intimacy Score: {self.report.relationship.intimacy}/100")
        if self.report.relationship.days > 0:
            progression_rate = self.report.relationship.intimacy / self.report.relationship.days
            lines.append(f"  Intimacy Progression: {progression_rate:.2f} points/day")
        lines.append("")

        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        for rec in self.report.recommendations:
            lines.append(f"  {rec}")
        lines.append("")

        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)

        return '\n'.join(lines)


def main():
    """Main simulation entry point"""
    import sys

    # Read log from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            log_text = f.read()
    else:
        log_text = sys.stdin.read()

    # Run simulation
    simulator = AiDPerformanceSimulator()
    report = simulator.parse_logs(log_text)

    # Generate and print report
    print(simulator.generate_report_text())

    # Optionally save JSON report
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            # Would need to implement JSON serialization for dataclasses
            pass


if __name__ == '__main__':
    main()
