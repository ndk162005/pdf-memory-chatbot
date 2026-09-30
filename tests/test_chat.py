import pytest
from app.llm.prompt_builder import PromptBuilder
from app.llm.conversation_manager import ConversationManager

def test_build_messages_with_context():
    builder = PromptBuilder()
    context = [{"text": "Fact 1"}]
    history = [{"role": "user", "content": "prev q"}, {"role": "assistant", "content": "prev a"}]
    msgs = builder.build_messages("my q", history, context)
    
    assert len(msgs) == 4  # system, user(hist), asst(hist), user(current)
    assert msgs[0]["role"] == "system"
    assert "Fact 1" in msgs[-1]["content"]
    assert "my q" in msgs[-1]["content"]

def test_build_messages_without_context():
    builder = PromptBuilder()
    msgs = builder.build_messages("my q", [], [])
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert "no context" in msgs[-1]["content"].lower() or "not find" in msgs[-1]["content"].lower()

def test_conversation_add_and_get():
    manager = ConversationManager()
    manager.add_message("s1", "user", "Hi")
    manager.add_message("s1", "assistant", "Hello")
    
    hist = manager.get_history("s1")
    assert len(hist) == 2
    assert hist[0]["role"] == "user"
    assert hist[1]["role"] == "assistant"

def test_conversation_max_messages_trim():
    manager = ConversationManager(max_messages=2)
    manager.add_message("s1", "user", "1")
    manager.add_message("s1", "assistant", "2")
    manager.add_message("s1", "user", "3")
    
    hist = manager.get_history("s1")
    assert len(hist) == 2
    assert hist[0]["content"] == "2"
    assert hist[1]["content"] == "3"

def test_resolve_followup_with_reference():
    manager = ConversationManager()
    manager.add_message("s1", "user", "What is Python?")
    manager.add_message("s1", "assistant", "A language.")
    
    q = manager.resolve_followup("s1", "Who created it?")
    assert "Python" in q

def test_resolve_followup_standalone_question():
    manager = ConversationManager()
    q = manager.resolve_followup("s1", "What is Java?")
    assert q == "What is Java?"

def test_clear_session():
    manager = ConversationManager()
    manager.add_message("s1", "user", "Hi")
    manager.clear_session("s1")
    assert manager.get_history("s1") == []

def test_prompt_contains_system_prompt():
    builder = PromptBuilder()
    msgs = builder.build_messages("q", [], [])
    assert msgs[0]["role"] == "system"
    assert len(msgs[0]["content"]) > 10
