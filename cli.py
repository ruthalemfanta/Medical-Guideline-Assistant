"""Command-line interface for the Medical Guideline Assistant."""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

import argparse
from src.medical_assistant import MedicalGuidelineAssistant


def main():
    """Main CLI function."""
    
    parser = argparse.ArgumentParser(
        description="Medical Guideline Assistant CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --query "What does WHO recommend for hypertension treatment?"
  python cli.py --add-document guidelines/who_hypertension_2023.pdf
  python cli.py --stats
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Ask a medical question"
    )
    
    parser.add_argument(
        "--add-document", "-a",
        type=str,
        help="Add a medical guideline PDF document"
    )
    
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show system statistics"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive mode"
    )
    
    args = parser.parse_args()
    
    # Initialize the assistant
    print("🏥 Medical Guideline Assistant")
    print("=" * 50)
    print("Initializing system...")
    
    assistant = MedicalGuidelineAssistant()
    print("✅ System ready")
    print("=" * 50)
    
    if args.query:
        # Process single query
        process_query(assistant, args.query)
        
    elif args.add_document:
        # Add document
        add_document(assistant, args.add_document)
        
    elif args.stats:
        # Show stats
        show_stats(assistant)
        
    elif args.interactive:
        # Interactive mode
        interactive_mode(assistant)
        
    else:
        parser.print_help()


def process_query(assistant: MedicalGuidelineAssistant, query: str):
    """Process a single query."""
    
    print(f"\n📝 Query: {query}")
    print("-" * 50)
    
    response = assistant.process_query(query)
    
    print(f"🤖 Answer:")
    print(response.answer)
    
    if response.citations:
        print(f"\n📚 Citations:")
        for i, citation in enumerate(response.citations, 1):
            print(f"{i}. {citation.guideline_name} ({citation.organization} {citation.year})")
            print(f"   Section: {citation.section}")
            if citation.page_number:
                print(f"   Page: {citation.page_number}")
            print(f"   Quote: {citation.quote[:100]}...")
            print()
    
    print(f"🎯 Confidence: {response.confidence_score:.2f}")
    print(f"🛡️ Safety Check: {'✅ Safe' if response.safety_check.is_safe else '❌ Unsafe'}")
    
    if response.safety_check.violations:
        print(f"⚠️ Violations: {', '.join(response.safety_check.violations)}")


def add_document(assistant: MedicalGuidelineAssistant, file_path: str):
    """Add a document to the system."""
    
    print(f"\n📄 Adding document: {file_path}")
    print("-" * 50)
    
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        return
    
    success = assistant.add_guideline_document(file_path)
    
    if success:
        print("✅ Document added successfully")
    else:
        print("❌ Failed to add document")


def show_stats(assistant: MedicalGuidelineAssistant):
    """Show system statistics."""
    
    print("\n📊 System Statistics")
    print("-" * 50)
    
    stats = assistant.get_system_stats()
    
    print(f"📚 Total Documents: {stats['total_documents']}")
    print(f"🏛️ Supported Sources: {', '.join(stats['supported_sources'])}")
    print(f"🛡️ Safety Checks: {'Enabled' if stats['safety_checks_enabled'] else 'Disabled'}")
    print(f"📝 Citations Required: {'Yes' if stats['citations_required'] else 'No'}")


def interactive_mode(assistant: MedicalGuidelineAssistant):
    """Start interactive mode."""
    
    print("\n🔄 Interactive Mode")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 50)
    
    while True:
        try:
            query = input("\n❓ Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            elif query.lower() in ['help', 'h']:
                print_help()
                continue
                
            elif query.lower() in ['stats', 's']:
                show_stats(assistant)
                continue
                
            elif not query:
                continue
            
            process_query(assistant, query)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def print_help():
    """Print interactive mode help."""
    
    print("\n📖 Available Commands:")
    print("  help, h     - Show this help")
    print("  stats, s    - Show system statistics")
    print("  quit, q     - Exit interactive mode")
    print("  <question>  - Ask a medical question")


if __name__ == "__main__":
    main()