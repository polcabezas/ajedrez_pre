# The Complete Chess Rulebook

## Table of Contents
- [Introduction](#introduction)
- [The Board and Initial Setup](#the-board-and-initial-setup)
- [Piece Movement Rules](#piece-movement-rules)
- [Basic Game Concepts](#basic-game-concepts)
- [Special Moves](#special-moves)
- [Game Conclusion](#game-conclusion)
- [Clock Rules and Time Controls](#clock-rules-and-time-controls)
- [Tournament Rules and Etiquette](#tournament-rules-and-etiquette)
- [Special and Edge Cases](#special-and-edge-cases)
- [Notation Systems](#notation-systems)
- [Rule Variations](#rule-variations)
- [Historical Developments](#historical-developments)

## Introduction

Chess is a two-player strategy board game played on a checkered 8×8 grid called a chessboard. The game represents a battle between two armies, each directed by a player. The objective is to place the opponent's king under direct attack with no legal move to escape (checkmate).

This document aims to cover all official chess rules as recognized by the International Chess Federation (FIDE), including standard rules, edge cases, special situations, and tournament regulations.

## The Board and Initial Setup

### The Board

1. The chessboard consists of 64 squares arranged in an 8×8 grid.
2. The squares alternate between light (white) and dark (black) colors.
3. The board is positioned so that a white square is in the right-hand corner nearest to each player.
4. The rows of squares running from one player to the other are called "files" (labeled a-h).
5. The rows running from left to right are called "ranks" (numbered 1-8).
6. Each square is identified by its file letter and rank number (e.g., "e4").

### Initial Setup

1. Each player begins with 16 pieces:
   - 1 king
   - 1 queen
   - 2 rooks
   - 2 bishops
   - 2 knights
   - 8 pawns

2. The pieces are arranged on the first two ranks as follows:
   - **First rank** (from left to right): rook, knight, bishop, queen, king, bishop, knight, rook
   - **Second rank**: all 8 pawns

3. White pieces occupy ranks 1 and 2; Black pieces occupy ranks 7 and 8.

4. The white queen starts on a white square (d1), and the black queen starts on a black square (d8).
   - Remember: "Queen on her color"

5. Official starting position in algebraic notation:
   - White: King on e1, Queen on d1, Rooks on a1 and h1, Bishops on c1 and f1, Knights on b1 and g1, Pawns on a2-h2
   - Black: King on e8, Queen on d8, Rooks on a8 and h8, Bishops on c8 and f8, Knights on b8 and g8, Pawns on a7-h7

## Piece Movement Rules

### King

1. Moves one square in any direction (horizontally, vertically, or diagonally).
2. Cannot move to a square under attack by an enemy piece.
3. Cannot move past an enemy piece.
4. May castle under specific conditions (see [Special Moves](#special-moves)).

### Queen

1. Moves any number of squares in any direction (horizontally, vertically, or diagonally).
2. Cannot jump over other pieces.
3. Captures by occupying the square of an enemy piece.

### Rook

1. Moves any number of squares horizontally or vertically.
2. Cannot jump over other pieces.
3. Captures by occupying the square of an enemy piece.
4. May participate in castling (see [Special Moves](#special-moves)).

### Bishop

1. Moves any number of squares diagonally.
2. Each bishop is confined to squares of the same color it starts on.
3. Cannot jump over other pieces.
4. Captures by occupying the square of an enemy piece.

### Knight

1. Moves in an "L" pattern: two squares horizontally or vertically followed by one square at a 90-degree angle.
2. Only piece that can jump over other pieces.
3. Captures by occupying the square of an enemy piece.

### Pawn

1. Moves forward one square (toward opponent's side of the board).
2. Cannot move backward.
3. On its first move, can advance two squares forward if both squares are unoccupied.
4. Captures by moving one square diagonally forward.
5. Cannot capture by moving straight ahead.
6. Subject to en passant captures (see [Special Moves](#special-moves)).
7. Can be promoted when reaching the opponent's back rank (see [Special Moves](#special-moves)).

## Basic Game Concepts

### Taking Turns

1. White always moves first, followed by Black, alternating turns.
2. A player must move on their turn; passing is not allowed.
3. A player may only move one piece per turn (except for castling).
4. A move is completed when:
   - The player has released a piece on a new square in a legal move
   - In the case of a capture, when the captured piece has been removed from the board and the player has released their own piece on its new square
   - In the case of castling, when the player has released both the king and rook
   - In the case of promotion, when the pawn has been removed, the new piece has been placed on the promotion square, and the player has released the new piece

### Captures

1. A piece captures an opponent's piece by moving to the square occupied by that piece.
2. The captured piece is removed from the board.
3. Capture is never mandatory (except in certain variants like Checkers/Draughts, which is not standard chess).

### Check

1. A king is in check when it is under attack by one or more enemy pieces.
2. When a king is in check, the player must make a move that removes the check.
3. There are three ways to remove a check:
   - Moving the king to a square not under attack
   - Capturing the attacking piece
   - Placing a piece between the king and the attacking piece (not possible with knight attacks)
4. A player cannot make a move that puts or leaves their own king in check.
5. A player is not required to announce "check" when putting the opponent's king under attack, though it is customary to do so.

## Special Moves

### Castling

1. The only move that allows two pieces (king and rook) to move during the same turn.
2. Requirements for castling:
   - Neither the king nor the rook involved has previously moved.
   - No pieces between the king and the rook.
   - The king is not in check.
   - The king does not pass through or finish on a square that is attacked by an enemy piece.
3. Procedure:
   - **Kingside castling** (O-O): The king moves two squares toward the h-file rook, and the rook moves to the square the king crossed (e.g., White: King e1→g1, Rook h1→f1).
   - **Queenside castling** (O-O-O): The king moves two squares toward the a-file rook, and the rook moves to the square the king crossed (e.g., White: King e1→c1, Rook a1→d1).
4. The king is moved first; if a player touches the rook first, they must move only the rook if legal (touch-move rule).

### En Passant

1. A special pawn capture that can occur when a pawn advances two squares from its starting position and lands adjacent to an opponent's pawn.
2. The opponent's pawn can capture the advanced pawn as if it had moved only one square.
3. Requirements:
   - The capturing pawn must be on the fifth rank (for White) or fourth rank (for Black).
   - The opponent's pawn must move two squares in one move (from its starting position).
   - The capture must be made immediately on the next move, or the right to capture en passant is lost.
4. The captured pawn is removed from the board as in a normal capture.
5. In algebraic notation, the capture is recorded as the destination square (not the square of the captured pawn), with "e.p." optionally added.

### Pawn Promotion

1. When a pawn reaches the eighth rank (for White) or first rank (for Black), it must be replaced by a queen, rook, bishop, or knight of the same color.
2. The choice is not limited to previously captured pieces; a player may have multiple queens, for example.
3. The new piece is placed on the square where the pawn reached the last rank.
4. Promotion is not limited to queen, though queen is most commonly chosen.
5. The promotion is part of the same move as the pawn's advance.
6. A player must promote the pawn, even if all resulting moves lead to disadvantage.
7. If the desired promotion piece is not physically available, the player may pause the clock and request assistance from the arbiter.

## Game Conclusion

### Checkmate

1. Occurs when a king is in check and there is no legal move to:
   - Move the king to a square not under attack
   - Capture the attacking piece
   - Block the attack
2. The player whose king is checkmated loses the game.
3. A player does not have to announce "checkmate"; the game ends when the position is reached.

### Stalemate

1. Occurs when a player has no legal moves, but their king is not in check.
2. Results in a draw.
3. Neither player wins or loses.

### Draw by Agreement

1. A game may be drawn if both players agree to a draw offer.
2. A player may offer a draw only after making a move and before pressing their clock.
3. The offer remains valid until the opponent rejects it, makes a move, or the offerer withdraws it.
4. If a player offers a draw before making a move, the offer is still valid but is considered a violation of the rules, and may be penalized by the arbiter.

### Draw by Insufficient Material

1. The game is drawn when neither player has sufficient material to force a checkmate.
2. Positions that are always drawn due to insufficient material:
   - King vs. King
   - King and Bishop vs. King
   - King and Knight vs. King
   - King and Bishop vs. King and Bishop with bishops on the same color
3. Positions that are generally drawn but where checkmate is theoretically possible:
   - King and two Knights vs. King (extremely rare and practically impossible without opponent's help)

### Draw by Threefold Repetition

1. A player may claim a draw if the same position has occurred three times with the same player to move.
2. The positions need not occur consecutively.
3. The right to castle or capture en passant must be the same each time for positions to be considered identical.
4. The claim must be made before making a move, or the right to claim is lost for that occurrence.
5. If the position occurs for a fifth time, the arbiter shall intervene and declare the game drawn.

### Draw by the Fifty-Move Rule

1. A player may claim a draw if the last 50 consecutive moves by each player have been made without:
   - Any pawn move
   - Any capture
2. The count resets after either event occurs.
3. The claim must be made before making a move, or the right to claim is lost for that occurrence.
4. If 75 moves are completed without a pawn move or capture, the arbiter shall intervene and declare the game drawn.

### Draw by Perpetual Check

1. There is no formal "perpetual check" rule in the FIDE Laws of Chess.
2. In practice, perpetual check situations are resolved through the threefold repetition rule.

### Resignation

1. A player may resign at any time, which results in a loss.
2. Resignation is typically indicated by:
   - Verbally announcing resignation
   - Tipping over the king
   - Extending a hand to the opponent
   - Signing the scoresheet
3. Once a resignation is properly communicated, it cannot be withdrawn.

### Abandonment

1. A player who leaves the playing area without permission or clear indication of resignation loses the game.
2. Exception: If the opponent cannot checkmate by any possible series of legal moves, the game is drawn.

## Clock Rules and Time Controls

### Basic Clock Usage

1. Each player has their own time allocation on a chess clock.
2. After making a move on the board, a player presses their clock, stopping their own time and starting their opponent's time.
3. A player may press their clock only after making a legal move.
4. Both hands must be used for castling before pressing the clock.

### Time Controls

1. **Classical/Standard**: Typically 60+ minutes per player.
2. **Rapid**: Typically 10-60 minutes per player.
3. **Blitz**: Typically 3-10 minutes per player.
4. **Bullet**: Less than 3 minutes per player.

### Increments and Delays

1. **Increment**: After each move, a predetermined amount of time is added to the player's clock.
2. **Delay/Bronstein**: A player's clock does not start counting down until after a predetermined delay.
3. **Simple Delay**: The clock pauses for a set time at the start of each turn.

### Time Forfeit

1. A player loses if their remaining time expires before completing their move, unless:
   - Their opponent cannot checkmate by any possible series of legal moves (draw)
   - Their opponent's flag has already fallen (depends on arbiter decision and rules of competition)
2. In games with increments, a player with very little time can potentially continue indefinitely by making moves quickly to accumulate time.

### Flag Fall

1. A player's "flag falls" when their time expires.
2. Digital clocks display "flag fall" in different ways (often with a flag symbol or flashing time display).
3. Only the players can claim a win on time; arbiters should refrain from pointing out flag falls.

### Irregularities

1. If a clock malfunctions, the arbiter replaces it and uses best judgment to establish times on the new clock.
2. If both players' flags have fallen and it is impossible to determine which fell first, the game continues (unless it is the last time control).
3. If a player knocks over pieces while press their clock, they must correct the position on their own time.

## Tournament Rules and Etiquette

### Starting the Game

1. If a player is absent at the start of the round:
   - For zero tolerance: The player loses immediately.
   - With a specified tolerance (e.g., 30 minutes): The player loses after that time elapses.
2. Players should shake hands before and after the game.
3. White pieces are typically determined by the tournament pairing system.

### Recording Moves

1. Each player must record all moves (both their own and their opponent's) using algebraic notation.
2. The scoresheet must be visible to the arbiter at all times.
3. Exceptions:
   - Players with less than 5 minutes remaining are not required to record moves.
   - Players with disabilities may receive special accommodation.
4. If a player fails to keep score, time may be deducted as a penalty.
5. Both players must sign both scoresheets at the end of the game, indicating the result.

### Touch-Move Rule

1. If a player deliberately touches a piece, they must move it if there is a legal move available.
2. If a player deliberately touches an opponent's piece, they must capture it if there is a legal way to do so.
3. If a player touches multiple pieces:
   - If they are all the player's pieces, the player must move the first piece touched that can be moved.
   - If they include both the player's and opponent's pieces, the player must capture with their piece the first opponent's piece touched that can be captured.
4. To adjust a piece on its square, the player must first say "j'adoube" or "I adjust."
5. If a player accidentally touches a piece or knocks it over, they are not obligated to move it.

### Illegal Moves

1. If an illegal move is discovered, the position before the irregularity must be reinstated.
2. If the position cannot be determined, the arbiter shall establish it by best judgment.
3. Penalties for illegal moves:
   - First illegal move: Additional time for the opponent (typically 2 minutes)
   - Second illegal move: Game loss for the offending player
   - In Rapid and Blitz, the first illegal move results in a loss unless specified otherwise by tournament regulations

### Using Both Hands

1. Players must use only one hand to move pieces.
2. Exception: Castling, which may be performed with both hands.
3. Pressing the clock must be done with the same hand used to move pieces.

### Behavior and Misconduct

1. Players may not:
   - Use any notes or outside information
   - Analyze on another board
   - Receive advice from others
   - Distract or annoy the opponent
   - Leave the playing area without permission
2. Players must not leave their mobile phones or electronic devices on in the playing area.
3. Violations can result in:
   - Warnings
   - Time penalties
   - Loss of the game
   - Expulsion from the tournament

### Appeals

1. Players can appeal decisions made by arbiters.
2. Appeals must typically be made in writing within a specified time.
3. An appeals committee, separate from the arbiter team, usually handles appeals.
4. The decision of the appeals committee is typically final.

## Special and Edge Cases

### Dead Position

1. A position is dead when no sequence of legal moves can lead to a checkmate by either player.
2. When a dead position occurs, the game is immediately drawn.
3. Examples include:
   - King vs. King
   - King and Bishop vs. King
   - King and Knight vs. King
   - King and Bishop vs. King and Bishop with bishops on the same color

### Three Knights Checkmate

1. With a King and three Knights vs. a lone King, checkmate is possible.
2. This is one of the rarest material combinations that can force checkmate.
3. However, it cannot arise in a regular game without promotion.

### Pawn Promotion Anomalies

1. Underpromotion (promoting to a piece other than a queen) is legal and sometimes strategically beneficial.
2. If a player advances a pawn to the promotion square and starts their opponent's clock without replacing the pawn with a promoted piece:
   - The move is illegal
   - The pawn must be replaced by a queen of the same color
3. A player may have multiple queens, rooks, bishops, or knights through promotion.
4. Theoretically, a player could have nine queens, ten rooks, ten bishops, or ten knights on the board simultaneously (original piece plus promotions).

### Impossible Positions

1. If a position is discovered that could not have been reached by any series of legal moves:
   - If discovered before both players have made 10 moves, the game is restarted.
   - If discovered after both players have made 10 moves, the game continues.
2. A player may not claim a win based on an impossible position.

### Sealed Moves (Historical)

1. In adjourned games, the player would seal their next move in an envelope.
2. Modern digital clocks have made adjournments and sealed moves rare in contemporary chess.
3. If a sealed move is illegal or ambiguous, the arbiter makes a determination according to the laws of chess.

### Adjacent Kings

1. The kings can never be on adjacent squares (including diagonally adjacent).
2. Any move that would result in the kings being adjacent is illegal.
3. This situation cannot legally arise in a chess game.

### Triple Check

1. There is no special "triple check" rule in official chess.
2. Some chess variants include a rule where delivering check with three pieces simultaneously results in an immediate win.

### Stalemate with Checkmate Threat

1. If a player's only legal move would expose their king to check, but they have no legal moves, the position is stalemate.
2. This results in a draw, even if the player would otherwise be checkmated on the next move.

### Forced vs. Unforced Draws

1. Some draws can be claimed by a player (threefold repetition, fifty-move rule).
2. Some draws are automatic (stalemate, insufficient material).
3. A player cannot refuse a forced draw.

### Zugzwang

1. A position where any move worsens the position for the player who must move.
2. Not a rule, but a positional concept in chess.
3. Can lead to stalemate or force a player to move into a worse position.

### Clock Failure

1. If a chess clock fails during a game, the arbiter must replace it.
2. The arbiter sets the new clock according to their best judgment.
3. If both flags have fallen and it is impossible to determine which fell first, the game continues unless it is the final time control phase.

### Game Interruption

1. If a game must be interrupted due to unforeseen circumstances (medical emergency, venue issues, etc.):
   - The arbiter stops the clocks.
   - The game resumes from the exact position when conditions permit.
   - The arbiter adjusts clock times as appropriate.

## Notation Systems

### Algebraic Notation (Standard)

1. Each square has a unique name based on file (a-h) and rank (1-8).
2. Pieces are denoted by capital letters:
   - K = King
   - Q = Queen
   - R = Rook
   - B = Bishop
   - N = Knight
   - Pawns have no letter designation
3. Captures are indicated by "x".
4. Check is indicated by "+".
5. Checkmate is indicated by "#" or "++".
6. Castling is indicated by "O-O" (kingside) or "O-O-O" (queenside).
7. Pawn promotion is indicated by "=" followed by the promoted piece.
8. When multiple pieces of the same type could move to the same square, clarification is provided by:
   - File of departure
   - Rank of departure
   - Both file and rank if necessary
9. En passant is indicated by "e.p." (optional).
10. Move evaluation symbols include:
    - ! = Good move
    - !! = Excellent move
    - ? = Poor move
    - ?? = Blunder
    - !? = Interesting move
    - ?! = Dubious move

### Descriptive Notation (Historical)

1. Each square is described from the perspective of each player.
2. Files are named after the pieces that start on them (K, Q, R, B, N, P).
3. The queen's side of the board is designated as "Q" and the king's side as "K".
4. Rarely used in modern chess but found in older literature.

### PGN (Portable Game Notation)

1. A standardized computer format for recording chess games.
2. Includes game metadata (players, date, event, etc.) and moves in algebraic notation.
3. Used for game databases and computer analysis.

### FEN (Forsyth-Edwards Notation)

1. A standard for describing a particular board position.
2. Contains information about:
   - Piece placement
   - Active color (whose turn it is)
   - Castling availability
   - En passant target square
   - Halfmove clock (for fifty-move rule)
   - Fullmove number
3. Primarily used in computer applications and for sharing specific positions.

## Rule Variations

### FIDE vs. USCF Rules

1. FIDE (International) and USCF (United States) rules have minor differences:
   - USCF allows more time before forfeiture for late arrival.
   - USCF has different time control categories.
   - USCF has different illegal move penalties in some cases.
2. Most core rules are identical between the two organizations.

### Historical Variations

1. Castling variations (e.g., allowing the king to jump over pieces).
2. Pawn initial movement (historically could only move one square).
3. The queen's movement (historically more limited).
4. Stalemate counting as a win for the player delivering it (in some historical variants).

### Online Chess Variations

1. Pre-move: Setting up a move to be played automatically on your next turn.
2. Auto-queen: Automatic promotion of pawns to queens.
3. Move confirmation: Option to require confirmation before a move is finalized.
4. Takebacks: Option to allow players to take back moves (by mutual agreement).

### Chess960 (Fischer Random Chess)

1. Starting position is randomized according to specific rules.
2. There are 960 possible starting positions (hence the name).
3. Castling rules are adapted to the starting position but maintain similar principles.
4. All other chess rules remain the same.

## Historical Developments

### Major Rule Changes

1. **Pawn Movement**: Originally moved only one square at a time. Two-square first move added around 13th-15th century.
2. **Queen Movement**: Originally could move only one square diagonally. Modern movement developed in late 15th century.
3. **Bishop Movement**: Originally could jump two squares diagonally. Modern diagonal movement developed around 15th century.
4. **Castling**: Standardized to current form around 17th century.
5. **En Passant**: Added when the two-square pawn move was introduced to prevent pawns from safely passing opposing pawns.
6. **Stalemate**: Has variously been counted as a win, loss, or draw. Standardized as a draw in the 19th century.

### The Touch-Move Rule Evolution

1. Not present in earliest forms of chess.
2. Implemented to prevent players from using piece-touching as a form of psychological warfare.
3. Formalized in tournament play in the 19th century.

### Time Controls

1. First chess clock invented in 1883 by Thomas Wilson.
2. Mechanical clocks with "flag fall" mechanism dominated until the late 20th century.
3. Digital clocks introduced in the 1970s and 1980s.
4. Time increments introduced with digital clocks, popularized by Bobby Fischer ("Fischer Clock").

### FIDE Rule Standardization

1. FIDE (Fédération Internationale des Échecs) established in 1924.
2. First unified international rules established in 1929.
3. Major revisions occurred in 1952, 1974, 1984, 1997, 2009, 2014, and 2018.
4. Zero tolerance for lateness (forfeiture for any lateness) introduced in 2009.

---

This document represents the comprehensive rules of chess as recognized by FIDE and major chess organizations worldwide. While chess has regional and historical variations, the rules presented here constitute the standard form of the game played in official competitions.

For official tournaments and competitions, always refer to the latest version of the FIDE Laws of Chess or the relevant governing body's rulebook, as specific regulations may be updated periodically.
