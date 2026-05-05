"""
SAGE: State-Aware Generative Engine

An experimental alternative to direct next-token reasoning.
Instead of asking a model to answer directly from long text,
SAGE asks a model to compile text into executable operations.
A deterministic state engine executes those operations,
verifies consistency, and renders the final answer.

Core hypothesis:
As context grows, verified state transitions degrade slower
than direct next-token answering.
"""

__version__ = "0.1.0"
