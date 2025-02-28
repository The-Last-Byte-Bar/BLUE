"""
Unit tests for the ContextBuilder class.

This module contains tests for the ContextBuilder class used for managing
conversation context in LLM interactions.
"""

import pytest
from datetime import datetime
import json

from llm.analysis import ContextBuilder


class TestContextBuilder:
    """Tests for the ContextBuilder class."""
    
    def test_create_context(self):
        """Test creating a new context."""
        builder = ContextBuilder()
        context_id = "test-context"
        
        result = builder.create_context(context_id)
        
        # Check that the context was created correctly
        assert result == context_id
        assert context_id in builder.contexts
        assert "created_at" in builder.contexts[context_id]
        assert "updated_at" in builder.contexts[context_id]
        assert "items" in builder.contexts[context_id]
        assert isinstance(builder.contexts[context_id]["created_at"], str)
        assert isinstance(builder.contexts[context_id]["updated_at"], str)
        assert isinstance(builder.contexts[context_id]["items"], list)
        assert len(builder.contexts[context_id]["items"]) == 0
    
    def test_create_context_overwrite(self):
        """Test creating a context that already exists."""
        builder = ContextBuilder()
        context_id = "test-context"
        
        # Create the context twice
        builder.create_context(context_id)
        original_created_at = builder.contexts[context_id]["created_at"]
        
        # Wait a moment to ensure timestamps differ
        import time
        time.sleep(0.01)
        
        builder.create_context(context_id)
        new_created_at = builder.contexts[context_id]["created_at"]
        
        # Check that the context was overwritten
        assert original_created_at != new_created_at
    
    def test_add_to_context(self):
        """Test adding content to a context."""
        builder = ContextBuilder()
        context_id = "test-context"
        builder.create_context(context_id)
        
        builder.add_to_context(context_id, "Test content", "user")
        
        # Check that the content was added correctly
        assert len(builder.contexts[context_id]["items"]) == 1
        item = builder.contexts[context_id]["items"][0]
        assert item["role"] == "user"
        assert item["content"] == "Test content"
        assert "added_at" in item
    
    def test_add_to_nonexistent_context(self):
        """Test adding content to a context that doesn't exist."""
        builder = ContextBuilder()
        context_id = "nonexistent-context"
        
        builder.add_to_context(context_id, "Test content", "user")
        
        # Check that the context was created automatically
        assert context_id in builder.contexts
        assert len(builder.contexts[context_id]["items"]) == 1
        item = builder.contexts[context_id]["items"][0]
        assert item["role"] == "user"
        assert item["content"] == "Test content"
    
    def test_get_context(self):
        """Test getting the contents of a context."""
        builder = ContextBuilder()
        context_id = "test-context"
        builder.create_context(context_id)
        
        # Add some items to the context
        builder.add_to_context(context_id, "User message 1", "user")
        builder.add_to_context(context_id, "Assistant response 1", "assistant")
        builder.add_to_context(context_id, "System message", "system")
        
        # Get the context
        context = builder.get_context(context_id)
        
        # Check that the context was returned correctly
        assert len(context) == 3
        assert context[0]["role"] == "user"
        assert context[0]["content"] == "User message 1"
        assert context[1]["role"] == "assistant"
        assert context[1]["content"] == "Assistant response 1"
        assert context[2]["role"] == "system"
        assert context[2]["content"] == "System message"
    
    def test_get_nonexistent_context(self):
        """Test getting a context that doesn't exist."""
        builder = ContextBuilder()
        context_id = "nonexistent-context"
        
        context = builder.get_context(context_id)
        
        # Check that an empty list was returned
        assert context == []
    
    def test_clear_context(self):
        """Test clearing a context."""
        builder = ContextBuilder()
        context_id = "test-context"
        builder.create_context(context_id)
        
        # Add some items to the context
        builder.add_to_context(context_id, "User message 1", "user")
        builder.add_to_context(context_id, "Assistant response 1", "assistant")
        
        # Clear the context
        builder.clear_context(context_id)
        
        # Check that the context was cleared
        assert context_id in builder.contexts
        assert len(builder.contexts[context_id]["items"]) == 0
    
    def test_clear_nonexistent_context(self):
        """Test clearing a context that doesn't exist."""
        builder = ContextBuilder()
        context_id = "nonexistent-context"
        
        # This should not raise an exception
        builder.clear_context(context_id)
    
    def test_delete_context(self):
        """Test deleting a context."""
        builder = ContextBuilder()
        context_id = "test-context"
        builder.create_context(context_id)
        
        # Delete the context
        builder.delete_context(context_id)
        
        # Check that the context was deleted
        assert context_id not in builder.contexts
    
    def test_delete_nonexistent_context(self):
        """Test deleting a context that doesn't exist."""
        builder = ContextBuilder()
        context_id = "nonexistent-context"
        
        # This should not raise an exception
        builder.delete_context(context_id) 