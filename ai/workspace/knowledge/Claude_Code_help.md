claude --help

Usage: claude [options] [command] [prompt]

  

Claude Code - starts an interactive session by default, use -p/--print for non-interactive output

  

Arguments:

  prompt                           Your prompt

  

Options:

  -d, --debug                      Enable debug mode

  --verbose                        Override verbose mode setting from config

  -p, --print                      Print response and exit (useful for pipes)

  --output-format <format>         Output format (only works with --print): "text" (default), "json" (single

                                   result), or "stream-json" (realtime streaming) (choices: "text", "json",

                                   "stream-json")

  --input-format <format>          Input format (only works with --print): "text" (default), or "stream-json"

                                   (realtime streaming input) (choices: "text", "stream-json")

  --mcp-debug                      [DEPRECATED. Use --debug instead] Enable MCP debug mode (shows MCP server

                                   errors)

  --dangerously-skip-permissions   Bypass all permission checks. Recommended only for sandboxes with no internet

                                   access.

  --allowedTools <tools...>        Comma or space-separated list of tool names to allow (e.g. "Bash(git:*)

                                   Edit")

  --disallowedTools <tools...>     Comma or space-separated list of tool names to deny (e.g. "Bash(git:*) Edit")

  --mcp-config <file or string>    Load MCP servers from a JSON file or string

  --append-system-prompt <prompt>  Append a system prompt to the default system prompt

  --permission-mode <mode>         Permission mode to use for the session (choices: "acceptEdits",

                                   "bypassPermissions", "default", "plan")

  -c, --continue                   Continue the most recent conversation

  -r, --resume [sessionId]         Resume a conversation - provide a session ID or interactively select a

                                   conversation to resume

  --model <model>                  Model for the current session. Provide an alias for the latest model (e.g.

                                   'sonnet' or 'opus') or a model's full name (e.g. 'claude-sonnet-4-20250514').

  --fallback-model <model>         Enable automatic fallback to specified model when default model is overloaded

                                   (only works with --print)

  --settings <file>                Path to a settings JSON file to load additional settings from

  --add-dir <directories...>       Additional directories to allow tool access to

  --ide                            Automatically connect to IDE on startup if exactly one valid IDE is available

  --strict-mcp-config              Only use MCP servers from --mcp-config, ignoring all other MCP configurations

  --session-id <uuid>              Use a specific session ID for the conversation (must be a valid UUID)

  -v, --version                    Output the version number

  -h, --help                       Display help for command

  

Commands:

  config                           Manage configuration (eg. claude config set -g theme dark)

  mcp                              Configure and manage MCP servers

  migrate-installer                Migrate from global npm installation to local installation

  setup-token                      Set up a long-lived authentication token (requires Claude subscription)

  doctor                           Check the health of your Claude Code auto-updater

  update                           Check for updates and install if available

  install [options] [target]       Install Claude Code native build. Use [target] to specify version (stable,

                                   latest, or specific version)

**Interactive Mode Commands:**

  **/add-dir** - Add a new working directory

  **/agents** - Manage agent configurations

  **/bug** - Submit feedback about Claude Code

  **/clear** - Clear conversation history and free up context

  **/compact** - Clear conversation history but keep a summary in context. Optional: /compact [instructions for

  summarization]

  **/config** - Open config panel

  **/cost** - Show the total cost and duration of the current session

  **/doctor** - Diagnose and verify your Claude Code installation and settings

  **/exit** - Exit the REPL

  **/export** - Export the current conversation to a file or clipboard

  **/help** - Show help and available commands

  **/hooks** - Manage hook configurations for tool events

  **/ide** - Manage IDE integrations and show status

  **/init** - Initialize a new CLAUDE.md file with codebase documentation

  **/install-github-app** - Set up Claude GitHub Actions for a repository

  **/login** - Sign in with your Anthropic account

  **/logout** - Sign out from your Anthropic account

  **/mcp** - Manage MCP servers

  **/memory** - Edit Claude memory files

  **/model** - Set the AI model for Claude Code

  **/permissions** - Manage allow & deny tool permission rules

  **/pr-comments** - Get comments from a GitHub pull request

  **/release-notes** - View release notes

  **/resume** - Resume a conversation

  **/review** - Review a pull request

  **/status** - Show Claude Code status including version, model, account, API connectivity, and tool statuses

  **/terminal-setup** - Enable Option+Enter key binding for newlines and visual bell

  **/upgrade** - Upgrade to Max for higher rate limits and more Opus

  **/vim** - Toggle between Vim and Normal editing modes