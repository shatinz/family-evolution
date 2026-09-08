#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Family Evolution
Provides autonomous tools for Claude Desktop, Claude Code, Antigravity, and AI Agents:
- Family status & longitudinal metrics
- 7-day weekly chore matrix & intelligent rotation
- Clinical evaluation logging & AI analysis reports
- Telegram broadcasting & automated database backups
"""
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import config
from data.database import (
    init_db,
    get_all_members,
    get_family_profile,
    get_stats_summary,
    get_today_chores_all,
    get_weekly_matrix,
    generate_schedule_for_days,
    rotate_chores_now,
    log_family_evaluation,
    get_systemic_health_trend,
    get_intervention_history
)
from brain.reporter import generate_weekly_analysis
from bot.telegram_bot import telegram_bot

# Setup logging to stderr so stdout remains clean for JSON-RPC
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("family_mcp")

# --- Tool Definitions ---
TOOLS = [
    {
        "name": "get_family_status",
        "description": "Get an overview of the family: active members, today's chore completion status, mood check-ins, and systemic psychological health trends.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of historical days to aggregate metrics for (default: 7)",
                    "default": 7
                }
            }
        }
    },
    {
        "name": "get_weekly_chore_matrix",
        "description": "Get the 7-day Persian chore matrix (Saturday to Friday) with member assignments, icons, rotational indicators, and completion statuses.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "week_offset": {
                    "type": "integer",
                    "description": "Week offset: 0 for current week, -1 for previous week, 1 for next week",
                    "default": 0
                }
            }
        }
    },
    {
        "name": "rotate_chores_schedule",
        "description": "Intelligently calculate and balance chore rotation schedules across family members based on cognitive and physical capability profiles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "Number of days ahead to generate/rotate schedules for (default: 7)",
                    "default": 7
                }
            }
        }
    },
    {
        "name": "generate_weekly_ai_report",
        "description": "Run the clinical systemic analysis: produces a detailed Leader Clinical Report, a supportive Family Broadcast text, and adaptive intervention recommendations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Evaluation window in days (default: 7)",
                    "default": 7
                }
            }
        }
    },
    {
        "name": "dispatch_telegram_broadcast",
        "description": "Broadcast a supportive notification, plan announcement, or reminder to all linked family members via Telegram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The broadcast message text to send to family members"
                }
            },
            "required": ["message"]
        }
    },
    {
        "name": "log_clinical_evaluation",
        "description": "Record a systemic psychological evaluation for a family member across 4 Likert scales (Psychological Safety, Respect, Perceived Care, Systemic Climate) + confidential narrative.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "member_id": {"type": "integer", "description": "ID of the family member evaluated"},
                "evaluation_type": {"type": "string", "enum": ["baseline", "monthly"], "default": "monthly"},
                "psychological_safety": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Psychological Safety score (1-5)"},
                "respect_status": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Respect and Status score (1-5)"},
                "perceived_care": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Perceived Care score (1-5)"},
                "overall_climate": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Overall Systemic Climate score (1-5)"},
                "narrative_text": {"type": "string", "description": "Confidential narrative text (kept strictly private for AI analysis)"}
            },
            "required": ["member_id", "psychological_safety", "respect_status", "perceived_care", "overall_climate"]
        }
    },
    {
        "name": "backup_database_to_telegram",
        "description": "Perform SQLite WAL checkpoint and send the full family.db file directly as a document to the admin's Telegram chat.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

# --- Tool Handlers ---

async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if name == "get_family_status":
            days = arguments.get("days", 7)
            profile = get_family_profile()
            members = get_all_members()
            today_chores = get_today_chores_all()
            stats = get_stats_summary(days=days)
            trends = get_systemic_health_trend()
            interventions = get_intervention_history(limit=3)
            
            result = {
                "family_profile": profile,
                "members_count": len(members),
                "members": [{"id": m["id"], "name_fa": m["name_fa"], "role": m["role"], "avatar": m["avatar"], "is_linked": bool(m["telegram_id"])} for m in members],
                "today_chores_total": len(today_chores),
                "today_chores_done": sum(1 for c in today_chores if c["status"] == "done"),
                "recent_stats": stats,
                "systemic_trends": trends,
                "active_interventions": interventions
            }
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

        elif name == "get_weekly_chore_matrix":
            week_offset = arguments.get("week_offset", 0)
            matrix = get_weekly_matrix(week_offset=week_offset)
            return {"content": [{"type": "text", "text": json.dumps(matrix, ensure_ascii=False, indent=2)}]}

        elif name == "rotate_chores_schedule":
            days_ahead = arguments.get("days_ahead", 7)
            res = rotate_chores_now(days_ahead=days_ahead)
            return {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}]}

        elif name == "generate_weekly_ai_report":
            days = arguments.get("days", 7)
            leader_report, family_broadcast, stats = generate_weekly_analysis(days=days)
            output = {
                "leader_report": leader_report,
                "family_broadcast": family_broadcast,
                "metrics_summary": stats
            }
            return {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False, indent=2)}]}

        elif name == "dispatch_telegram_broadcast":
            msg = arguments.get("message", "")
            if not msg:
                return {"isError": True, "content": [{"type": "text", "text": "Error: message argument is required"}]}
            res = await telegram_bot.dispatch_custom_broadcast(msg)
            return {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}]}

        elif name == "log_clinical_evaluation":
            eval_id = log_family_evaluation(
                member_id=arguments["member_id"],
                evaluation_type=arguments.get("evaluation_type", "monthly"),
                psychological_safety=arguments["psychological_safety"],
                respect_status=arguments["respect_status"],
                perceived_care=arguments["perceived_care"],
                overall_climate=arguments["overall_climate"],
                narrative_text=arguments.get("narrative_text", "")
            )
            return {"content": [{"type": "text", "text": json.dumps({"status": "ok", "evaluation_id": eval_id})}]}

        elif name == "backup_database_to_telegram":
            res = await telegram_bot.send_database_backup_to_admin()
            return {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}]}

        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}

    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}", exc_info=True)
        return {"isError": True, "content": [{"type": "text", "text": f"Execution error in {name}: {str(e)}"}]}

# --- Stdio JSON-RPC MCP Server Protocol ---

def run_mcp_server():
    logger.info("Starting Family Evolution MCP Stdio Server...")
    init_db(seed_defaults=False)
    
    for line in sys.stdin:
        line_str = line.strip()
        if not line_str:
            continue
        
        try:
            req = json.loads(line_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Malformed JSON: {e}")
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # 1. Initialize
        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "family-evolution",
                        "version": "2.6.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        # 2. Notifications initialized / ping
        elif method == "notifications/initialized":
            pass # No response required for notifications
        
        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        # 3. Tools List
        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        # 4. Tools Call
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            call_res = asyncio.run(handle_tool_call(tool_name, tool_args))
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": call_res
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        else:
            if req_id is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    run_mcp_server()
