#!/usr/bin/env python3
"""
CLI for Shadow First Skill

Usage:
    python -m grilo_admin.skills.cli check <concept>
    python -m grilo_admin.skills.cli shadow <concept>
    python -m grilo_admin.skills.cli ritual
    python -m grilo_admin.skills.cli status
    python -m grilo_admin.skills.cli report <theme>
"""

import sys
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from grilo_admin.skills import ShadowFirstSkill, ConceptRegistry


def cmd_check(args):
    """Check a concept's documentation status."""
    skill = ShadowFirstSkill()
    result = skill.check(args.concept)

    print(f"\n{'='*60}")
    print(f"SHADOW CHECK: {args.concept}")
    print(f"{'='*60}")
    print(f"Status: {result['status']}")
    print(f"Registered: {result['registered']}")
    if result.get('shadow_score') is not None:
        print(f"Shadow Score: {result['shadow_score']}%")
    print(f"Recommendation: {result.get('recommendation', 'N/A')}")
    print()


def cmd_shadow(args):
    """Start shadow documentation for a concept."""
    skill = ShadowFirstSkill()
    session = skill.shadow(args.concept)

    print(f"\n{'='*60}")
    print(f"SHADOW SESSION: {args.concept}")
    print(f"{'='*60}")
    print(f"Started: {session.started_at}")
    print(f"Has content: {session.shadow_doc is not None}")
    print(f"FAQs: {len(session.faqs)}")
    print(f"Gaps: {len(session.gaps)}")
    print()


def cmd_add_content(args):
    """Add shadow document content."""
    skill = ShadowFirstSkill()
    skill.add_shadow_content(args.concept, args.content, sources=args.sources)
    print(f"✅ Content added for: {args.concept}")


def cmd_add_faq(args):
    """Add an FAQ entry."""
    skill = ShadowFirstSkill()
    skill.add_faq(args.concept, args.question, args.answer)
    print(f"✅ FAQ added for: {args.concept}")


def cmd_complete(args):
    """Complete a shadow session."""
    skill = ShadowFirstSkill()
    skill.complete_session(args.concept)
    print(f"✅ Session completed for: {args.concept}")


def cmd_ritual(args):
    """Run pre-session ritual."""
    skill = ShadowFirstSkill()
    result = skill.ritual()

    print(f"\n{'='*60}")
    print("SHADOW RITUAL - Pre-Session Check")
    print(f"{'='*60}")
    print(f"Total concepts: {result['total_concepts']}")
    print(f"Shadow debt: {result['shadow_debt_count']}")
    print(f"Avg Shadow Score: {result['avg_shadow_score']}%")

    if result['shadow_debt']:
        print(f"\n⚠️  SHADOW DEBT:")
        for item in result['shadow_debt']:
            print(f"   • {item['concept']} ({item['priority']} priority)")
            print(f"     First mentioned: {item['first_mentioned']}")

    if result['recommendations']:
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"   {rec['message']}")

    print()


def cmd_status(args):
    """Get overall status."""
    skill = ShadowFirstSkill()
    result = skill.status()

    print(f"\n{'='*60}")
    print("SHADOW STATUS")
    print(f"{'='*60}")
    print(f"Total concepts: {result['total_concepts']}")
    print(f"Complete: {result['complete']} ({result['completeness_pct']}%)")
    print(f"Partial: {result['partial']}")
    print(f"Undocumented: {result['undocumented']}")
    print(f"Avg Shadow Score: {result['avg_shadow_score']}%")

    if result['complete_concepts']:
        print(f"\n✅ Complete:")
        for c in result['complete_concepts']:
            print(f"   • {c}")

    if result['partial_concepts']:
        print(f"\n⚠️  Partial:")
        for c in result['partial_concepts']:
            print(f"   • {c}")

    if result['shadow_debt_concepts']:
        print(f"\n❌ Shadow Debt:")
        for c in result['shadow_debt_concepts']:
            print(f"   • {c}")

    print()


def cmd_report(args):
    """Generate a session report."""
    skill = ShadowFirstSkill()
    report = skill.generate_report(args.theme, args.concepts.split(',') if args.concepts else [])

    print(f"\n{'='*60}")
    print(f"SHADOW REPORT: {args.theme}")
    print(f"{'='*60}")
    print(f"Generated: {report['generated_at']}")
    print(f"Concepts documented: {report['concepts_mentioned']}")
    print(f"Shadow debt resolved: {report['shadow_debt_resolved']}")

    if report['gaps_identified']:
        print(f"\nGaps identified:")
        for gap in report['gaps_identified']:
            print(f"   • {gap}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Shadow First CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # check
    p_check = subparsers.add_parser("check", help="Check concept documentation status")
    p_check.add_argument("concept", help="Concept to check")
    p_check.set_defaults(func=cmd_check)

    # shadow
    p_shadow = subparsers.add_parser("shadow", help="Start shadow session")
    p_shadow.add_argument("concept", help="Concept to document")
    p_shadow.set_defaults(func=cmd_shadow)

    # add-content
    p_add = subparsers.add_parser("add-content", help="Add shadow content")
    p_add.add_argument("concept", help="Concept name")
    p_add.add_argument("content", help="Content to add")
    p_add.add_argument("--sources", nargs="+", help="Sources used")
    p_add.set_defaults(func=cmd_add_content)

    # add-faq
    p_faq = subparsers.add_parser("add-faq", help="Add FAQ entry")
    p_faq.add_argument("concept", help="Concept name")
    p_faq.add_argument("question", help="Question")
    p_faq.add_argument("--answer", help="Answer")
    p_faq.set_defaults(func=cmd_add_faq)

    # complete
    p_complete = subparsers.add_parser("complete", help="Complete shadow session")
    p_complete.add_argument("concept", help="Concept to complete")
    p_complete.set_defaults(func=cmd_complete)

    # ritual
    p_ritual = subparsers.add_parser("ritual", help="Pre-session shadow debt check")
    p_ritual.set_defaults(func=cmd_ritual)

    # status
    p_status = subparsers.add_parser("status", help="Overall shadow status")
    p_status.set_defaults(func=cmd_status)

    # report
    p_report = subparsers.add_parser("report", help="Generate session report")
    p_report.add_argument("theme", help="Session theme")
    p_report.add_argument("--concepts", help="Comma-separated concept list")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
