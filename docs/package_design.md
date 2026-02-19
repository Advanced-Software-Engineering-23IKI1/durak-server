# Package design

This file introduces a structure definition for the packages forming the backbone of the client-server communication.
Example JSONs that are provided are meant as a reference, not test JSONs as they contain invalid elements such as comments.


### general package structure


A package is defined as a valid JSON string containing a package `type` as well as a `body` which holds the package specific information.

The ASCII record seperator (`\x1e`, ASCII 30) is used to seperate individual JSON objects.

example JSON:
```json
{
	"type":	"name",
	"body":
	{
        // package specific information
	}
}
```


# Client -> Server

packages sent from client to server

<details>
<summary>overview</summary>

| Package Type                                        | Game Stage  | Sent On    | Max Times Sent |
|-----------------------------------------------------|-------------|------------|----------------|
| [start-game-session](#start-game-session)           | before game | event      | 1              |
| [connect-to-game-session](#connect-to-game-session) | before game | event      | 1[^1]          |
| [status-update](#status-update)                     | lobby       | event      | N              |
| [player-attack](#player-attack)                     | game        | event      | N              |
| [player-defense](#player-defense)                   | game        | event      | N              |
| [player-surrender](#player-surrender)               | game        | event      | N              |

[^1]: package can be sent N times but only once succefully.

</details>



### pre-game start

packages sent pre-game and pre-lobby

<div id="start-game-session">
<details>
<summary>start game session</summary>

This package is sent when a <ins>new</ins> game session is initiated.
The package initiates AND joins the player in the session.
`playername` can be any string. Any validation is to be performed server-side but is not currently planned.
This package is sent only once and is event-driven.

Example JSON:
```json
{
	"type":	"start-game-session",
	"body":
	{
		"playername":	"passcht_03"
	}
}
```
</details>
</div>

<div id="connect-to-game-session">
<details>
<summary>connect to game session</summary>

This package is sent when a player wants to connect to an <ins>existing</ins> game session.
The `gamecode` is a string validated on the server side.
`playername` can be any string. Any validation is to be performed server-side but is not currently planned.
This package is sent only once and is event-driven.

```json
{
    "type":	"connect-to-game-session",
	"body":
	{
		"gamecode":	"A0313",
		"playername":	"passcht_03"
	}
}
```
</details>
</div>


### lobby loop
packages sent in the lobby.

<div id="status-update">
<details>
<summary>status update</summary>

This package is sent when a individual player changes their 'readiness' status.
It can be sent N times per player and is event-driven.

```json
{
	"type":	"status-update",
	"body":
	{
		"is-ready": true
	}
}
```
</details>
</div>


### game loop

<div id="player-attack">
<details>
<summary>player attack</summary>

This package is sent when a player 
- initiates an attack
- joins an attack
- "forwards" an attack (dependant on ruleset used)

```json
{
	"type":	"player-attack",
	"body":
	{
		"cards": [1, 3, 12, 17]  // array of card ids
	}
}
```
</details>
</div>


<div id="player-defense">
<details>
<summary>player defense</summary>

This package is sent when a player defends a attack card with a defense card.
Up to N cards may be defended in the same package.
Already defended cards are not re-sent via this package.

```json
{
	"type":	"player-defense",
	"body":
	{
		"defense": [
            {
                "attack_id": 2,
                "defend_id": 4
            },
            {
                "attack_id": 3,
                "defend_id": 6
            }
        ]
	}
}
```
</details>
</div>

<div id="player-surrender">
<details>
<summary>player surrender</summary>

This package is sent when a player surrenders and picks up all attacking cards

```json
{
	"type":	"player-surrender",
	"body": {}
}
```
</details>
</div>




# Server -> Client

<details>
<summary>overview</summary>

| Package Type                                              | Game Stage | Sent On    | Max Times Sent | Personalized |
|-----------------------------------------------------------|------------|------------|----------------|--------------|
| [exception](#exception)                                   | global     | event      | N              | -            |
| [lobby-status](#lobby-status)                             | lobby      | event      | N              | no           |
| [game-config](#game-config)                               | lobby      | event      | N              | no           |
| [game-start](#game-start)                                 | lobby      | event      | 1              | no           |
| [player-hands-update](#player-hands-update)               | game       | event      | N              | yes          |
| [player-status-update](#player-status)                    | game       | event      | N              | no           |
| [table-update](#table-update)                             | game       | event      | N              | no           |
| [end-routine](#table-update)                              | end        | event      | 1              | no           |

</details>


### general

<div id="exception">
<details>
<summary>Exception</summary>

This package is sent to the client when an exception occurs.
`details` is an object with an undertermined structure and provides additional information depending on the specific exception that occured. 

```json
{
    "type": "exception",
    "body": {
        "name": "gamecode-not-found",
        "details": {}  //additional exception details
    }
}
```

</details>
</div>




### lobby loop

<div id="lobby-status">
<details>
<summary>lobby-status</summary>

This package is sent periodically to indicate the current status of the lobby.

```json
{
    "type": "lobby-status",
    "body": {
        "gamecode": "A0313",
        "players": [
            {
                "playername": "player1",
                "player_id": 9,
                "is-ready": true
            },
            {
                "playername": "player2",
                "player_id": 0,
                "is-ready": false
            }
        ]
    }
}
```
</details>
</div>


<div id="game-config">
<details>
<summary>game-config</summary>

This package is sent once before game start and every time the config is updated.

```json
{
    "type": "game-config",
    "body": {
        "cards": [  // card groups ordered from lowest -> highest (card strength is NOT determined by value attribute)
            [  // lowest card strength(s) . This list may also hold up to N card objects to allow for multi card deck games
                // trump cards are ommitted here as they are stronger
                {
                    "value": "2",  // card value (for display)
                    "suit": "hearts",
                    "id": 12
                },
                {
                    "value": "2",
                    "suit": "diamonds",
                    "id": 12
                },
                {
                    "value": "2",
                    "suit": "spades",
                    "id": 12
                },
            ],
            [
                {
                    "value": "3",
                    "suit": "hearts",
                    "id": 18
                },
                {
                    "value": "3",
                    "suit": "diamonds",
                    "id": 21
                },
                {
                    "value": "3",
                    "suit": "spades",
                    "id": 39
                },
            ],
            [  // trump card(s) are ranked above all other cards. !important: this array can also have up to K elements due to multiple decks 
                {
                    "value": "2",
                    "suit": "clubs",
                    "id": 17
                },
            ]
        ],

    },
    "attack-forwarding": {  // attack forwarding rules
        "is-enabled": true,  // global enable/disable
        "exact-count-match": false  // whether the exact amount of card attacking has to be matched for forwarding
    },
    "player-card-count": 7,  // amount of cards each player receives
    "all-card-defend-early-end": false
}
```
</details>
</div>




<div id="game-start">
<details>
<summary>game-start</summary>

This package is sent to indicate a game start.

```json
{
    "type": "game-start",
    "body": {
    }
}
```
</details>
</div>



### game loop

<div id="player-hands-update">
<details>
<summary>player-hands-update</summary>

This package is sent on event to update player hand and other miscellaneous stats

```json
{
    "type": "player-hands-update",
    "body": {
        "hand": [1,5,43,89],  // player hand card ids
        "player-hands": [  // card count of opponent player hands, ordered in playing order
            {
                "player_id": 2,
                "card_count": 9
            },
            {
                "player_id": 9,
                "card_count": null  //!! null if player is finished, 0 can be reached in attack but player has to draw, so 0 != null !!
            }
        ],
        "draw-pile": 12, // amount of cards on the draw pile (trump card NOT included)
        "trump": 3, // trump card id; if the card id drawn this attribute is set to null.
        "player-order": [2, 0, 1, 3, 7]  // player-ids in order (non-participating players [finished/disconnected] are ommitted)
    }
}
```
</details>
</div>

<div id="player-status">
<details>
<summary>player-status</summary>

This package is sent on event to broadcast the current player status.
Valid status strings are
- "attack"
- "defend"
- "finish"

```json
{
    "type": "player-status",
    "body": {
        "statuses": [
            {
                "player_id": 8,
                "status": "attack"
            },
            {
                "player_id": 5,
                "status": "defend"
            },
            {
                "player_id": 9,
                "status": "finished"
            }
        ]
    }
}
```
</details>
</div>

<div id="table-update">
<details>
<summary>table-update</summary>

This package is sent to update the cards on the table.

```json
{
    "type": "table-update",
    "body": {
        "table-state": [
            {
                "attack_id": 8,
                "from_player": 9,
                "defend_id": 7
            },
            {
                "attack_id": 19,
                "from_player": 0,
                "defend_id": null
            }
        ]
    }
}
```
</details>
</div>


### end routine

<div id="end-routine">
<details>
<summary>end-routine</summary>

This package is sent on game completion for the leaderboard

```json
{
    "type": "end-routine",
    "body": {
        "scoreboard": [4,2,7,9,2,9]  // ordered array of player ids (first->last place)
    }
}
```
</details>
</div>

### exception packages

All packages may include additional attributes in the `details` and should be parsed based purely based on the name.


<div id="PackageParsingExceptionPackage">
<details>
<summary>PackageParsingExceptionPackage</summary>

```json
{
    "type": "exception",
    "body": {
        "name": "PackageParsingException",
        "details": {
            "stage": "JSON",  // stage of package decoding ('JSON', 'Package-Type', 'Body')
            "raw_msg": ""  // raw error message
        }
    }
}
```

</details>
</div>


<div id="InvalidGameCodeExceptionPackage">
<details>
<summary>InvalidGameCodeExceptionPackage</summary>

```json
{
    "type": "exception",
    "body": {
        "name": "InvalidGameCodeExceptionPackage",
        "details": {
            "code": ""  // game code provided
        }
    }
}
```

</details>
</div>

<div id="InvalidCardIdExceptionPackage">
<details>
<summary>InvalidCardIdExceptionPackage</summary>

Sent if a card id is invalid

```json
{
    "type": "exception",
    "body": {
        "name": "InvalidCardIdExceptionPackage",
        "details": {
            "card_id": [3,4]  // card(s) that player attempted to use
        }
    }
}
```

</details>
</div>


<div id="CardIdNotInPossessionExceptionPackage">
<details>
<summary>CardIdNotInPossessionExceptionPackage</summary>

Sent if a card_id that is being used is not in the player's posession

```json
{
    "type": "exception",
    "body": {
        "name": "CardIdNotInPossessionExceptionPackage",
        "details": {
            "card_id": [3,4]  // card(s) that player attempted to use
        }
    }
}
```

</details>
</div>
