"""
Interactive docstring generation prompts.

Position
--------
Handles user interaction for human-provided docstring content.
Uses rich library for terminal UI.

Invariants
----------
- Graceful handling of Ctrl+C
- Session save/resume support
- Non-interactive mode available
"""

from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from rdf.observe.models import (
    FunctionProfile,
    GeneratedDocstring,
    HumanInput,
    InferredInvariant,
    InferredPosition,
)

console = Console()


@dataclass
class InteractiveSession:
    """
    Interactive session for docstring generation.

    Position
    --------
    Orchestrates the user interaction flow for each function.

    Invariants
    ----------
    - One function at a time
    - Always shows auto-inferred before prompting
    - Supports skip, edit, apply actions
    """

    profiles: dict[str, FunctionProfile]
    inferences: dict[str, tuple[InferredPosition, list[InferredInvariant]]]
    non_interactive: bool = False

    def run(self) -> list[GeneratedDocstring]:
        """Run interactive session for all functions."""
        generated = []
        functions = list(self.profiles.items())
        total = len(functions)

        console.print(f"\n[bold]Generating docstrings for {total} functions[/bold]")
        if not self.non_interactive:
            console.print("Use --non-interactive to skip prompts\n")

        for i, (qualname, profile) in enumerate(functions, 1):
            inference = self.inferences.get(qualname)
            if not inference:
                continue

            position, invariants = inference

            try:
                result = self._process_function(i, total, qualname, profile, position, invariants)
                if result:
                    generated.append(result)
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted. Progress saved.[/yellow]")
                break

        return generated

    def _process_function(
        self,
        index: int,
        total: int,
        qualname: str,
        profile: FunctionProfile,
        position: InferredPosition,
        invariants: list[InferredInvariant],
    ) -> GeneratedDocstring | None:
        """Process a single function interactively."""
        # Header
        console.print(f"\n{'━' * 60}")
        console.print(f"[bold cyan]Function {index}/{total}: {qualname}[/bold cyan]")
        console.print(f"📍 {profile.file_path}:{profile.line_number}")
        console.print(f"{'━' * 60}")

        # Show auto-inferred
        self._display_inferred(position, invariants, profile)

        if self.non_interactive:
            # Auto-generate without prompts
            human_input = HumanInput()
        else:
            # Prompt for human input
            human_input = self._prompt_human_input(profile)

            if human_input is None:  # User chose to skip
                return None

        # Build generated docstring
        first_obs = profile.observations[0] if profile.observations else None

        # Convert arguments tuple to dict
        inferred_params = {}
        if first_obs:
            inferred_params = dict(first_obs.arguments)

        generated = GeneratedDocstring(
            qualname=qualname,
            file_path=profile.file_path,
            line_number=profile.line_number,
            inferred_position=position,
            inferred_invariants=invariants,
            inferred_params=inferred_params,
            inferred_return=first_obs.return_value if first_obs else None,
            human_input=human_input,
        )

        # Preview
        console.print("\n[bold]Generated Docstring:[/bold]")
        console.print(
            Panel(
                Syntax(f'"""\n{generated.render()}\n"""', "python", theme="monokai"),
                title="Preview",
                border_style="green",
            )
        )

        if self.non_interactive:
            return generated

        # Action prompt
        console.print("\n[dim][a]pply  [e]dit  [s]kip  [q]uit[/dim]")
        action = Prompt.ask(
            "[bold]Action[/bold]",
            choices=["a", "e", "s", "q"],
            default="a",
        )

        if action == "a":  # Apply
            return generated
        elif action == "e":  # Edit
            # Re-prompt
            return self._process_function(index, total, qualname, profile, position, invariants)
        elif action == "s":  # Skip
            return None
        elif action == "q":  # Quit
            raise KeyboardInterrupt

        return None

    def _display_inferred(
        self,
        position: InferredPosition,
        invariants: list[InferredInvariant],
        profile: FunctionProfile,
    ) -> None:
        """Display auto-inferred information."""
        console.print("\n[bold green]Auto-Inferred:[/bold green]")

        # Position info
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="dim")
        table.add_column("Value")

        table.add_row("Role", position.structural_role.value)
        if position.call_graph_description:
            table.add_row("Call Graph", position.call_graph_description)
        if position.io_description:
            table.add_row("I/O", position.io_description)
        table.add_row("Observations", str(len(profile.observations)))

        console.print(table)

        # Invariants
        if invariants:
            console.print("\n[bold]Invariants:[/bold]")
            for inv in invariants:
                confidence_pct = int(inv.confidence * 100)
                console.print(
                    f"  • {inv.description} "
                    f"[dim]({confidence_pct}%, {inv.observations_count} obs)[/dim]"
                )

    def _prompt_human_input(self, profile: FunctionProfile) -> HumanInput | None:
        """Prompt user for human-provided content."""
        console.print("\n[bold yellow]Human Input:[/bold yellow]")

        # Business purpose (required)
        purpose = Prompt.ask(
            "\n? [bold]Business purpose[/bold] (what does this do for users/business?)",
            default="",
        )

        if not purpose:
            if Confirm.ask("No purpose provided. Skip this function?", default=True):
                return None
            return self._prompt_human_input(profile)

        # Architectural context (optional)
        context = Prompt.ask(
            "? [bold]Architectural context[/bold] "
            "(why here? design rationale?) [dim][Enter to skip][/dim]",
            default="",
        )

        # Additional invariants (optional)
        additional = Prompt.ask(
            "? [bold]Additional invariants[/bold] "
            "the code SHOULD enforce? [dim][Enter to skip][/dim]",
            default="",
        )
        additional_list = [inv.strip() for inv in additional.split(",") if inv.strip()]

        return HumanInput(
            business_purpose=purpose,
            architectural_context=context or None,
            additional_invariants=additional_list,
        )
