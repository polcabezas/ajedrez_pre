# The Comprehensive Laws of Chess

This document outlines the rules of chess, based on the official FIDE Laws of Chess. It aims to be exhaustive, covering standard play, special moves, game completion, irregularities, and common tournament practices.

**Note:** For official tournament play, the absolute latest version of the FIDE Laws of Chess handbook should always be consulted. This document serves as a detailed guide.

---

## Article 1: The Nature and Objectives of the Game

1.1 **The Game:** Chess is played between two opponents moving pieces alternately on a square board called a 'chessboard'.

1.2 **Starting Player:** The player with the light-coloured pieces ('White') makes the first move. The player with the dark-coloured pieces ('Black') makes the next move. The right to move alternates between players.

1.3 **Objective:** The objective of each player is to place the opponent's King 'under attack' in such a way that the opponent has no legal move to avoid the King being captured on the next move.

1.4 **Checkmate:** The player who achieves this objective is said to have 'checkmated' the opponent's King and has won the game. Leaving one's own King under attack, exposing one's own King to attack, and 'capturing' the opponent's King are not allowed.

1.5 **Draw:** If the position is such that neither player can possibly checkmate the opponent's King, the game is drawn (see Article 5.2.2 and Article 9.6 for more details).

---

## Article 2: The Initial Position of the Pieces on the Chessboard

2.1 **The Chessboard:** The chessboard is composed of an 8x8 grid of 64 equal squares alternately light (the 'white' squares) and dark (the 'black' squares). It is placed between the players such that the near right corner square is light.

2.2 **The Pieces:** At the beginning of the game, one player has 16 light-coloured pieces (the 'White' pieces); the other has 16 dark-coloured pieces (the 'Black' pieces). These pieces are:
    *   One White King (symbol: K)
    *   One White Queen (symbol: Q)
    *   Two White Rooks (symbol: R)
    *   Two White Bishops (symbol: B)
    *   Two White Knights (symbol: N)
    *   Eight White Pawns (symbol: P, often omitted in notation)
    *   One Black King (symbol: k)
    *   One Black Queen (symbol: q)
    *   Two Black Rooks (symbol: r)
    *   Two Black Bishops (symbol: b)
    *   Two Black Knights (symbol: n)
    *   Eight Black Pawns (symbol: p, often omitted in notation)

2.3 **Initial Setup:** The initial position of the pieces on the chessboard is as follows:
    *   The row ('rank') nearest each player holds the major pieces. From left to right (for White): Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook.
    *   The Queen stands on the square of her own colour (White Queen on a light square, Black Queen on a dark square).
    *   The row ('rank') immediately in front of the major pieces holds the eight Pawns.
    *   The diagram below shows the standard starting position:

        ```
        +---+---+---+---+---+---+---+---+
        8 | r | n | b | q | k | b | n | r |
        +---+---+---+---+---+---+---+---+
        7 | p | p | p | p | p | p | p | p |
        +---+---+---+---+---+---+---+---+
        6 |   |   |   |   |   |   |   |   |
        +---+---+---+---+---+---+---+---+
        5 |   |   |   |   |   |   |   |   |
        +---+---+---+---+---+---+---+---+
        4 |   |   |   |   |   |   |   |   |
        +---+---+---+---+---+---+---+---+
        3 |   |   |   |   |   |   |   |   |
        +---+---+---+---+---+---+---+---+
        2 | P | P | P | P | P | P | P | P |
        +---+---+---+---+---+---+---+---+
        1 | R | N | B | Q | K | B | N | R |
        +---+---+---+---+---+---+---+---+
          a   b   c   d   e   f   g   h
        ```
        *(Lowercase = Black, Uppercase = White)*

---

## Article 3: The Moves of the Pieces

3.1 **General Movement:**
    *   No piece can be moved to a square occupied by a piece of the same colour.
    *   If a piece moves to a square occupied by an opponent's piece, the latter is 'captured' and removed from the chessboard as part of the same move.
    *   A piece is said to attack an opponent's piece if it could make a capture on that square according to Articles 3.2 to 3.8.
    *   A piece is considered to attack a square even if such a piece is constrained from moving to that square because it would then leave or place the King of its own colour under attack.

3.2 **The Bishop (B):** The Bishop may move to any square along a diagonal on which it stands, provided the path is clear. It cannot jump over other pieces.

3.3 **The Rook (R):** The Rook may move to any square along the file (vertical column) or the rank (horizontal row) on which it stands, provided the path is clear. It cannot jump over other pieces. (See also Article 3.10 on Castling).

3.4 **The Queen (Q):** The Queen combines the moves of the Rook and the Bishop. It may move to any square along the file, rank, or diagonal on which it stands, provided the path is clear. It cannot jump over other pieces.

3.5 **The Knight (N):** The Knight moves in an 'L' shape: two squares horizontally then one square vertically, OR two squares vertically then one square horizontally. The Knight's move is *not* blocked by other pieces; it is the only piece that can 'jump' over other pieces. It always lands on a square of the opposite colour from its starting square.

3.6 **The Pawn (P):** Pawns move differently from how they capture.
    *   **Movement:** Pawns move forward only.
        *   From its initial position (2nd rank for White, 7th rank for Black), a pawn has the option of moving forward one square *or* two squares, provided both squares are unoccupied.
        *   After its first move, a pawn can only move forward one square at a time, provided the square is unoccupied.
    *   **Capture:** A pawn captures diagonally forward one square. It captures by moving to the square occupied by the opponent's piece, which is then removed.
    *   **Special Pawn Moves:** See Article 3.7 (En Passant) and Article 3.8 (Promotion).

3.7 **The Pawn - En Passant Capture:**
    *   **Condition:** When a player's pawn moves two squares forward from its starting position, and lands on the same rank adjacent to an opponent's pawn, the opponent's pawn has the option of capturing the advanced pawn *as if* the latter had only moved one square forward.
    *   **Execution:** This capture must be made *only on the very next move* following the two-square pawn advance. If the opponent does not exercise this option immediately, the right to do so is lost.
    *   **Mechanics:** The capturing pawn moves diagonally forward to the square the advanced pawn *would have occupied* if it had only moved one square. The advanced pawn is removed from the board.
    *   **Example:** White pawn on e2 moves to e4. If there is a Black pawn on d4 or f4, Black (on the *immediately* following move only) can capture the White e4-pawn by moving their pawn to e3. The White e4-pawn is removed.

3.8 **The Pawn - Promotion:**
    *   **Condition:** When a pawn reaches the rank furthest from its starting position (the 8th rank for White, the 1st rank for Black), it *must* be exchanged *as part of the same move* for a new piece of the player's choice: a Queen, Rook, Bishop, or Knight of the *same colour* as the pawn.
    *   **Choice:** The player's choice is not restricted to pieces that have already been captured. Any of the four piece types can be chosen.
    *   **Effect:** The new piece's effect is immediate. For example, if a pawn promotes to a Queen and delivers checkmate, the game ends instantly.
    *   **Impossibilities:** A pawn cannot remain a pawn on the final rank. A pawn cannot be promoted to a King.

3.9 **The King (K):**
    *   **Movement:** The King can move one square in any direction (horizontally, vertically, or diagonally) to a square that is not attacked by one or more of the opponent's pieces.
    *   **Capturing:** The King captures like it moves, by moving to a square occupied by an opponent's piece.
    *   **Check:** The King is said to be 'in check' if it is attacked by one or more of the opponent's pieces, even if such pieces are constrained from moving (pinned).
    *   **Restrictions:** A player must never make a move that places or leaves their own King in check.
    *   **Special Move - Castling:** See Article 3.10.

3.10 **The King - Castling:** Castling is a special move involving the King and one of the Rooks of the same colour, counting as a single King move. It consists of moving the King two squares towards a Rook on the player's first rank, then placing that Rook on the square the King just crossed.
    *   **Conditions for Castling:** Castling is illegal if:
        1.  The King has previously moved, OR
        2.  The Rook chosen for castling has previously moved.
        Furthermore, castling is temporarily prevented if:
        3.  There are any pieces between the King and the chosen Rook.
        4.  The King is currently in check.
        5.  The square the King must cross over is attacked by an opponent's piece.
        6.  The square the King lands on is attacked by an opponent's piece.
    *   **Types of Castling:**
        *   **Kingside Castling (Short Castling):** With the Rook on the h-file. The King moves two squares (from e1 to g1 for White, e8 to g8 for Black), and the Rook moves to the square the King crossed (from h1 to f1 for White, h8 to f8 for Black). Notation: `O-O`.
        *   **Queenside Castling (Long Castling):** With the Rook on the a-file. The King moves two squares (from e1 to c1 for White, e8 to c8 for Black), and the Rook moves to the square the King crossed (from a1 to d1 for White, a8 to d8 for Black). Notation: `O-O-O`.
    *   **Clarifications on Lost Castling Rights:**
        *   If the King moves, castling rights (both kingside and queenside) are permanently lost.
        *   If a Rook moves, castling rights are permanently lost *for that specific Rook*. The player might still be able to castle with the other Rook if its rights are intact.
        *   Castling rights are lost even if the King or Rook returns to its original square.
        *   Temporarily being unable to castle (e.g., because a square is attacked, or pieces are in the way) does *not* remove the right to castle later if the conditions become favourable again, provided the King and relevant Rook haven't moved.
        *   **Edge Case:** If a Rook is captured on its starting square (e.g., h1) without having moved, the right to castle with that Rook is obviously lost.

---

## Article 4: The Act of Moving the Pieces

4.1 **Alternating Moves:** Each move must be made with one hand only.

4.2 **Touch-Move Rule (Strictly applied in tournaments):**
    *   **Touching Own Piece:** If a player, having the move, deliberately touches one or more of their own pieces, they must move the first piece touched that can be legally moved.
    *   **Touching Opponent's Piece:** If a player deliberately touches one or more of the opponent's pieces, they must capture the first piece touched that can be legally captured.
    *   **Touching Own then Opponent's Piece:** If a player deliberately touches one of their own pieces and then one of the opponent's pieces, they must make the capture if it is legal. If the capture is illegal, they must move the first touched own piece if it has a legal move; if not, they must capture the first touched opponent's piece with another piece if legal. If neither is possible, the player is free to make any legal move.
    *   **Touching Multiple Pieces:** If it's unclear whether the player touched their own or the opponent's piece first, it's assumed they touched their own piece first. If a player touches multiple pieces of their own colour, they must move the first one touched that has a legal move. If a player touches multiple pieces of the opponent's colour, they must capture the first one touched that can be legally captured.
    *   **Castling:** Castling is considered a King move. Therefore, if intending to castle, the King *must* be touched and moved first (two squares). If the Rook is touched first, a Rook move must be made instead, forfeiting castling with that Rook. If the player touches the King and Rook simultaneously intending to castle, castling must be performed if legal.
    *   **Pawn Promotion:** If a player moves a pawn to the promotion rank and releases it, they must promote it. The move is not complete until the new piece is placed on the promotion square. Touching the pawn does not commit the player to promoting until it reaches the final rank. If the player removes the pawn and presses the clock before placing the new piece, the move is illegal.
    *   **J'adoube / I Adjust:** A player may adjust one or more pieces on their squares, provided they first express their intention (for example, by saying "j'adoube" or "I adjust") *before* touching the piece(s). This does not apply if the player has already deliberately touched a piece with the apparent intention to move it.

4.3 **Completed Move:** A move is considered completed when:
    *   The piece has been moved to its destination square and the player's hand has released the piece.
    *   In case of a capture, the captured piece has been removed from the board, the player has placed their own piece on its new square, and the player's hand has released the piece.
    *   In case of castling, the player's hand has released the Rook on the square crossed by the King. If the player releases the King first, the move is not yet completed, but the player no longer has the right to make any other move except castling (if legal). If castling is illegal, the player must make another legal King move if possible (including returning the King to its original square if no other King move is legal).
    *   In case of pawn promotion, the pawn has been removed, the new piece placed on the promotion square, and the player's hand has released the new piece. If the player releases the pawn on the promotion square, the move is not complete, but the player loses the right to move the pawn to another square. The move is completed when the new piece is placed.

4.4 **Illegal Moves:** If a player makes an illegal move:
    *   The position must be reset to what it was immediately before the illegal move.
    *   If the piece moved illegally was touched according to the touch-move rule (Article 4.2), that piece must be moved if it has a legal move. If the illegal move was castling, the King must be moved if it has a legal move (possibly including castling with the other Rook). If the piece (or King in illegal castling) has no legal move, the player may make any other legal move.
    *   For the first completed illegal move by a player, the arbiter shall give two minutes extra time to the opponent. For the second completed illegal move by the same player, the arbiter shall declare the game lost by this player. However, the game is drawn if the position is such that the opponent cannot checkmate the player's king by any possible series of legal moves. (This penalty primarily applies in standard/rapid play; Blitz rules differ - see Appendix A).
    *   **Edge Case - Not noticing illegal move:** If an illegal move is completed, and the opponent makes their next move without pointing out the illegality, the illegal move generally stands in standard play (FIDE 7.5.5), and the game continues from the new position. *However*, this can be complex and depend on arbiter intervention and specific tournament rules. Blitz rules are stricter (see Appendix A).

---

## Article 5: The Completion of the Game

5.1 **Win:** The game is won by the player:
    *   Who has checkmated the opponent's King. This immediately ends the game.
    *   Whose opponent declares they resign. This immediately ends the game.
    *   Whose opponent exceeds the time limit (runs out of time on their clock), provided the player has sufficient mating material (see below). This immediately ends the game unless Article 5.2 applies (draw due to insufficient material).
    *   Whose opponent makes a second illegal move (in standard/rapid play, see Article 4.4 and 7.5.5).
    *   Whose opponent refuses to comply with the rules or arbiter's instructions.
    *   **Sufficient Mating Material:** A player is considered to have sufficient mating material to win on time if there exists *any possible series of legal moves* by which they could checkmate the opponent (even if highly improbable or requiring opponent's blunders).
        *   Examples of sufficient material: K+Q vs K, K+R vs K, K+B+N vs K, K+P vs K (if the pawn can promote).
        *   Examples of insufficient material: K vs K, K+N vs K, K+B vs K.
        *   If the player claiming the win on time has insufficient material, the game is a draw.
    *   **Edge Case Win on Time:** If Player A's time expires, but Player B cannot possibly checkmate Player A *by any sequence of legal moves* (even with worst play from Player A), the game is a DRAW, not a win for B (e.g., B only has K+N or K+B left).

5.2 **Draw:** The game is drawn:
    *   **Stalemate:** When the player whose turn it is has no legal move, and their King is *not* in check. This immediately ends the game.
    *   **Agreement:** When both players agree to a draw during the game. This immediately ends the game. A draw offer is typically made after making a move and before pressing the clock. The offer is valid until the opponent accepts, rejects, or makes their own move.
    *   **Threefold Repetition:** When the *exact same position* is about to appear or has appeared for the third time, with the *same player* to move. Positions are considered the same if the same types of pieces occupy the same squares, the same moves are available to both players (including rights to castle or capture en passant). If a player intends to make a move that results in the third repetition, they should write the move on their scoresheet, declare the intention to claim the draw to the arbiter, and *then* make the move. If the position has already occurred twice before, the player whose turn it is can claim the draw *before* making any move. The claim must be verified by the arbiter.
    *   **Fifty-Move Rule:** When the last 50 consecutive moves have been made by each player without any pawn move and without any capture. A player can claim a draw under this rule. If the player intends to make a move that results in the 50th move without pawn move or capture, they should write the move, declare the claim, and make the move. If the 50 moves have already passed, the player whose turn it is can claim the draw before making a move. The claim must be verified.
    *   **Impossibility of Checkmate (Insufficient Material):** When a position arises from which no possible sequence of legal moves can lead to checkmate for either player (even with the most unskilled play). This immediately ends the game. Common examples:
        *   King vs King (K vs K)
        *   King and Bishop vs King (K+B vs K)
        *   King and Knight vs King (K+N vs K)
        *   King and Bishop vs King and Bishop, with both Bishops on squares of the same colour (K+B vs K+B same color).
        *   **Edge Cases for Insufficiency:**
            *   K+N+N vs K: This is *theoretically* sufficient material to force mate, but it's extremely difficult and often results in a draw by the 50-move rule or repetition if the lone King plays correctly. FIDE rules often automatically declare it drawn in practice under specific tournament conditions or by arbiter discretion if no progress is being made, though technically it's not *always* impossible.
            *   Positions where mate is technically possible but requires very specific, unlikely sequences might still be declared drawn by an arbiter under certain conditions if no progress is being made towards mate (linked to 50-move rule).
    *   **Draw on Time:** If a player's flag falls (time runs out), but the opponent cannot possibly checkmate the player by any series of legal moves (has insufficient mating material), the game is a draw.

---

## Article 6: The Chess Clock

6.1 **Purpose:** A 'chess clock' is a device with two time displays, connected so that only one can run at a time. 'Clock' means one of the two time displays. 'Flag fall' means the expiration of the allotted time for a player.

6.2 **Usage:**
    *   Each player must make a set number of moves or all moves in an allotted period of time. This can include additional time (increment) added after each move.
    *   The player must press the clock with the same hand used to make the move. It is forbidden to keep a finger on the clock button or hover over it.
    *   Players must handle the clock properly; pressing it too violently or knocking it over may incur penalties.
    *   If a player is unable to use the clock (e.g., disability), an assistant acceptable to the arbiter may operate it.

6.3 **Time Controls:** Common types include:
    *   **Standard/Classical:** Longer time limits (e.g., 90 minutes for 40 moves + 30 minutes for rest of game, with 30-second increment per move). Requires notation.
    *   **Rapid:** Shorter time limits (e.g., 15 minutes + 10 seconds increment, or 25 minutes total). Notation may or may not be required depending on exact time.
    *   **Blitz:** Very short time limits (e.g., 3 minutes + 2 seconds increment, or 5 minutes total). Notation is generally not required. Special rules apply (see Appendix A).
    *   **Bullet:** Extremely short time limits (e.g., 1 minute total). Often played online, follows Blitz rules.

6.4 **Flag Fall:** Except where Articles 5.1 (Win) and 5.2 (Draw conditions like stalemate, agreement, repetition, 50-move, impossibility) apply, if a player does not complete the prescribed number of moves in the allotted time, the game is lost by the player. However, the game is drawn if the position is such that the opponent cannot checkmate the player's king by any possible series of legal moves (insufficient mating material).

---

## Article 7: Irregularities

7.1 **Incorrect Setup:** If during the game it is found that the initial position of the pieces was incorrect, the game shall be cancelled and a new game played. If discovered *after* the game started, the game continues unless the arbiter decides otherwise.

7.2 **Incorrect Board Placement:** If the chessboard has been placed contrary to Article 2.1 (white square right corner), the game continues, but the position reached must be transferred to a correctly placed chessboard.

7.3 **Pieces Displaced:** If pieces are accidentally displaced or knocked over, the player whose turn it is should restore the correct position on their own time. If necessary, clocks can be paused. If discovered later, the game should be reconstructed to the position before the displacement if possible.

7.4 **Illegal Moves (Recap & Penalty):** See Article 4.4. First offense usually warning + time penalty (2 min to opponent in Standard/Rapid), second offense is loss of game. Blitz rules differ.

7.5 **Check Not Announced:** Announcing "check" is customary but not required by the rules. A player does not gain any rights from their opponent's failure to announce check.

---

## Article 8: The Recording of the Moves (Notation)

8.1 **Requirement:** In games with longer time controls (Standard, most Rapid), each player is obliged to record their own moves and those of the opponent, move after move, as clearly and legibly as possible, in the algebraic notation, on the scoresheet prescribed for the competition.

8.2 **Algebraic Notation:**
    *   Each square is identified by a unique coordinate (letter a-h for file, number 1-8 for rank).
    *   Piece names are abbreviated: K (King), Q (Queen), R (Rook), B (Bishop), N (Knight). Pawns are not indicated by a letter, only by the arrival square.
    *   **Move:** Piece letter (except pawns) + arrival square (e.g., `Nf3`, `Be5`, `c5`).
    *   **Capture:** Piece letter (except pawns) + `x` + arrival square (e.g., `Bxc6`, `Nxd4`, `exd5`). Pawn captures include the departure file (e.g., `exd5`). If ambiguity exists for pieces (two Knights can move to f3), specify departure rank or file (e.g., `Nbd2`, `N8d7`, `Rfe1`).
    *   **Check:** Add `+` (e.g., `Qb4+`).
    *   **Checkmate:** Add `#` (e.g., `Qh7#`).
    *   **Kingside Castling:** `O-O`.
    *   **Queenside Castling:** `O-O-O`.
    *   **En Passant Capture:** Notation is as if the pawn moved to the capture square (e.g., if White pawn on e5 captures Black pawn moving d7-d5 en passant, it's `exd6`). Sometimes `e.p.` is added.
    *   **Pawn Promotion:** Arrival square + `=` + promoted piece letter (e.g., `e8=Q`).

8.3 **Scoresheet Use:** The scoresheet is primarily for recording moves but also used for draw claims (repetition, 50-move), noting time, etc. It belongs to the tournament organizer.

8.4 **When to Write:** Moves should ideally be written down *before* making the move, but making the move then writing it immediately is common practice. A draw offer is written with `(=)`.

8.5 **Less than 5 Minutes:** If a player has less than five minutes left on their clock in a time period without increment, they are not obliged to keep score.

---

## Article 9: The Drawn Game (Recap & Details)

9.1 **Agreement:** See Article 5.2 (Draws).

9.2 **Threefold Repetition:** See Article 5.2 (Draws). The claim must be made correctly (ideally before or just as the move creating the repetition is made). If the claim is incorrect, the arbiter may award the opponent extra time.

9.3 **Fifty-Move Rule:** See Article 5.2 (Draws). The claim process is similar to repetition.

9.4 **Stalemate:** See Article 5.2 (Draws). Ends game automatically.

9.5 **Insufficient Material:** See Article 5.2 (Draws). Ends game automatically if recognized.

9.6 **No Possibility of Winning:** The game is drawn if a position is reached from which a checkmate cannot occur by any possible series of legal moves, even with the most unskilled play. This immediately ends the game. (This formalizes the insufficient material rule mentioned in Article 5.2).

---

## Article 10: Points (Scoring in Competitions)

10.1 Typically: Win = 1 point, Draw = ½ point, Loss = 0 points. Variations exist (e.g., 3 points for a win).

---

## Article 11: The Conduct of the Players

11.1 **Fair Play:** Players shall take no action that will bring the game of chess into disrepute.

11.2 **No Assistance:** Players are forbidden from using any notes, sources of information, or advice, or analyzing on another board during play. Scoresheets are only for recording moves, times, draw offers, and claim details.

11.3 **No Distraction/Annoyance:** Players must not distract or annoy the opponent in any manner whatsoever. This includes unreasonable claims, persistent draw offers, or distracting behaviour.

11.4 **Electronic Devices:** Mobile phones and other electronic devices capable of communication or analysis are strictly forbidden in the playing venue. Penalties are severe, often resulting in immediate loss of game. Specific tournament rules dictate whether devices can be stored (switched off) in a bag or must be left outside entirely.

11.5 **Leaving the Venue:** Players are generally not allowed to leave the playing venue without permission from the arbiter.

11.6 **Penalties:** Penalties for rule infractions can range from warnings, time additions for the opponent, time deductions for the offender, loss of the game, or expulsion from the event.

---

## Article 12: The Role of the Arbiter

12.1 The arbiter ensures the Laws of Chess are strictly observed.

12.2 The arbiter acts in the best interest of the competition, ensuring fair play and a good playing environment.

12.3 The arbiter supervises the competition, resolves disputes, imposes penalties, pairs players, etc.

12.4 Arbiter decisions are generally final, though appeal processes may exist.

---

## Appendix A: Rapid Chess Rules (Main Differences)

A.1 Rapid chess is a game where either all moves must be completed in a fixed time of more than 10 minutes but less than 60 minutes for each player; or the time allotted + 60 times any increment is more than 10 minutes but less than 60 minutes for each player.

A.2 Players are not required to record the moves.

A.3 Penalties for illegal moves are often stricter or applied differently than in Standard (e.g., first illegal move might lose the game if claimed by the opponent before they move). Check specific tournament rules.

---

## Appendix B: Blitz Chess Rules (Main Differences)

B.1 Blitz chess is a game where all moves must be completed in a fixed time of 10 minutes or less for each player; or the allotted time + 60 times any increment is 10 minutes or less.

B.2 Notation is not required.

B.3 **Illegal Moves in Blitz:** An illegal move is completed once the opponent's clock has been started. The opponent is entitled to claim a win *before making their own move*. However, if the opponent cannot checkmate the player's king by any possible series of legal moves, then the claimant is entitled to claim a draw. If the opponent does not claim and makes a move, the illegal move stands and the game continues.

B.4 **Touch-Move:** Strict touch-move applies (Article 4).

B.5 **Flag Fall:** Article 6 (Clock) and 5.1 (Win on time) apply. A player can claim a win on time if their opponent's flag falls, *provided the player themselves has mating material*. If the player claiming also has insufficient mating material, it's a draw.

---

## Important Edge Cases and Improbable Scenarios Summarized

*   **Castling Through Check:** Illegal. The square the King crosses *cannot* be attacked.
*   **Castling Into Check:** Illegal. The square the King lands on *cannot* be attacked.
*   **Castling When King is In Check:** Illegal.
*   **Castling After King/Rook Moved:** Illegal, even if returned to original square.
*   **En Passant Timing:** Only available on the *immediately* following move.
*   **Pawn Promotion Choice:** Must be Q, R, B, or N of the *same color*. Cannot remain pawn, cannot become King. Choice is instant. If a player places the promoted piece upside down (e.g. an inverted Rook sometimes used for a Queen if none is handy), its identity is determined by what the player *intended* or *declared*, or defaults to Queen if unclear. Best practice is to pause the clock and find the correct physical piece.
*   **Claiming Repetition/50-Move Draw:** Must be done correctly, usually involves stopping clocks and calling arbiter. Incorrect claim may be penalized.
*   **Two Kings Next to Each Other:** Impossible in a legal game. This can only happen if one or more preceding illegal moves went unnoticed and uncorrected. The position should be reconstructed to before the *first* illegal move occurred.
*   **Promoting to Opponent's Piece Color:** Illegal.
*   **Moving Two Pieces at Once:** Illegal (except castling).
*   **Skipping a Turn:** Illegal.
*   **Capturing Own Piece:** Illegal.
*   **Leaving King in Check at End of Move:** Illegal.
*   **Moving a Pinned Piece to Expose King:** Illegal.
*   **What if both flags fall?** In case of uncertainty about which flag fell first (without electronic clocks accurately recording it), the arbiter usually declares a draw or orders the game to continue with remaining time if applicable. Modern electronic clocks resolve this.
*   **Checkmate/Stalemate Unnoticed:** The game *legally ended* the moment the checkmate or stalemate position occurred on the board, even if players continue moving in ignorance. Once noticed, the result stands as of the move that created the mate/stalemate.

---

This document attempts to be a comprehensive guide to the rules of chess. Remember that subtle interpretations and specific tournament regulations can sometimes add further layers, always deferring to the official FIDE Laws and the chief arbiter's judgment in formal settings.