# Software Defect Triage and Repair Planner

## Overview

This project is an AI-assisted defect triage and repair planning system. It ingests bug reports, detects duplicates, analyzes root causes, prioritizes issues, and generates repair plans and acceptance scenarios using a structured AI prompt pipeline.

## Key Capabilities

* Bug report submission and validation
* Duplicate detection using similarity analysis
* Priority recommendation with rationale
* Root cause inference with confidence scoring
* Repair plan generation with test-first approach
* Acceptance scenario generation (Gherkin-based)
* Failure bundle summarization
* Release risk analysis

## Architecture Approach

The system follows an acceptance-test-driven AI development pipeline:
Use Case → Gherkin Contracts → Implementation → Failure Analysis → Minimal Patch Repair

## Tech Stack

* Node.js + Express (Backend)
* SQLite (Database)
* Prisma ORM
* Cucumber.js (Acceptance Testing)
* Jest (Unit Testing)
* Python (Automation Agent)
* OpenAI API (AI Services)
* GitHub (Version Control)

## Purpose

This project demonstrates AI-assisted software engineering using reusable prompt templates, deterministic acceptance testing, and automated defect lifecycle management.
