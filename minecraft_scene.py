#!/usr/bin/env python3
"""Minecraft Scene Generator — procedural Minecraft-style pixel art."""

import os
import random
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw

# ── Dimensions ────────────────────────────────────────────────────────────────
BLOCK = 8   # pixels per block (pre-scale)
W = 80      # world width  (blocks)
H = 50      # world height (blocks)
SP = 2      # sprite pixel size in native pixels

# ── Block IDs ─────────────────────────────────────────────────────────────────
AIR=0; GRASS=1; DIRT=2; STONE=3; BEDROCK=4; WATER=5
SAND=6; SANDSTONE=7; OAK_LOG=8; OAK_LEAVES=9
SPRUCE_LOG=10; SPRUCE_LEAVES=11; CACTUS=12; SNOW=13
COAL=14; IRON=15; GOLD=16; DIAMOND=17; LAVA=18
JUNGLE_LOG=19; JUNGLE_LEAVES=20; BIRCH_LOG=21; BIRCH_LEAVES=22
PLANKS=23; COBBLE=24; GLASS=25

# ── Palette ───────────────────────────────────────────────────────────────────
PALETTE = {
    GRASS:         ( 88, 120,  52),
    DIRT:          (139,  98,  66),
    STONE:         (122, 122, 122),
    BEDROCK:       ( 48,  48,  48),
    WATER:         ( 52, 102, 192),
    SAND:          (219, 208, 151),
    SANDSTONE:     (198, 186, 124),
    OAK_LOG:       (102,  82,  51),
    OAK_LEAVES:    ( 68, 108,  44),
    SPRUCE_LOG:    ( 88,  68,  44),
    SPRUCE_LEAVES: ( 44,  88,  44),
    CACTUS:        ( 52, 120,  52),
    SNOW:          (238, 242, 248),
    COAL:          (122, 122, 122),
    IRON:          (112, 102,  92),
    GOLD:          (140, 122,  78),
    DIAMOND:       ( 90, 128, 148),
    LAVA:          (218,  58,   0),
    JUNGLE_LOG:    ( 96,  76,  48),
    JUNGLE_LEAVES: ( 54, 134,  38),
    BIRCH_LOG:     (198, 188, 162),
    BIRCH_LEAVES:  (100, 128,  68),
    PLANKS:        (177, 144,  83),
    COBBLE:        (108, 108, 108),
    GLASS:         (175, 210, 225),
}

ORE_SPOTS = {
    COAL:    ( 26,  26,  26),
    IRON:    (180, 140, 104),
    GOLD:    (218, 186,  48),
    DIAMOND: ( 76, 208, 210),
}

SKY_COLORS = {
    "day":    (106, 162, 250),
    "sunset": (248, 148,  72),
    "night":  ( 10,  12,  44),
}

BIOMES = ["forest", "desert", "snow", "plains", "jungle"]
TIMES  = ["day", "sunset", "night"]

SURF_BLOCK = {
    "forest": GRASS, "plains": GRASS,
    "jungle": GRASS, "snow": SNOW, "desert": SAND,
}

TREE_PARAMS = {
    "forest": (3, 6,  OAK_LOG,    OAK_LEAVES,    "round",      8),
    "plains": (3, 5,  BIRCH_LOG,  BIRCH_LEAVES,  "round",      3),
    "jungle": (7, 12, JUNGLE_LOG, JUNGLE_LEAVES, "round",      7),
    "snow":   (4, 8,  SPRUCE_LOG, SPRUCE_LEAVES, "triangular", 8),
    "desert": (0, 0,  CACTUS,     CACTUS,        "cactus",    10),
}

# ── Sprite color shorthands ───────────────────────────────────────────────────
N  = None                # transparent
SK = (200, 155, 100)     # skin
BL = ( 60, 100, 180)     # blue shirt
JE = ( 50,  80, 140)     # jeans
DK = ( 22,  22,  22)     # dark / black
CG = ( 88, 168,  88)     # creeper green
ZG = ( 80, 160,  80)     # zombie green skin
CY = ( 52, 148, 148)     # zombie cyan shirt
BO = (208, 202, 192)     # skeleton bone
PK = (228, 168, 168)     # pig pink
RD = (200,  50,  50)     # red (eyes / chicken comb)
BR = (120,  80,  40)     # cow brown
WH = (230, 230, 230)     # white
YL = (230, 185,  50)     # chicken yellow
EK = ( 18,  18,  18)     # enderman black
PU = (130,  60, 210)     # enderman purple
VL = (185, 155, 115)     # villager skin
VR = (120,  78,  28)     # villager robe

# ── Sprite sheets (8 cols × N rows, drawn bottom-up from surface) ─────────────
SPRITES = {
    "steve": [
        [N,  SK, SK, SK, SK, SK, SK, N ],
        [SK, SK, SK, SK, SK, SK, SK, SK],
        [SK, SK, DK, SK, SK, DK, SK, SK],
        [SK, SK, DK, SK, SK, DK, SK, SK],
        [SK, SK, SK, SK, SK, SK, SK, SK],
        [SK, SK, SK, SK, SK, SK, SK, SK],
        [SK, BL, BL, BL, BL, BL, BL, SK],
        [SK, BL, BL, BL, BL, BL, BL, SK],
        [SK, BL, BL, BL, BL, BL, BL, SK],
        [SK, BL, BL, BL, BL, BL, BL, SK],
        [SK, BL, BL, BL, BL, BL, BL, SK],
        [SK, BL, BL, BL, BL, BL, BL, SK],
        [N,  JE, JE, N,  N,  JE, JE, N ],
        [N,  JE, JE, N,  N,  JE, JE, N ],
        [N,  JE, JE, N,  N,  JE, JE, N ],
        [N,  JE, JE, N,  N,  JE, JE, N ],
    ],
    "creeper": [
        [N,  CG, CG, CG, CG, CG, CG, N ],
        [CG, CG, CG, CG, CG, CG, CG, CG],
        [CG, DK, DK, CG, CG, DK, DK, CG],
        [CG, DK, DK, CG, CG, DK, DK, CG],
        [CG, CG, CG, DK, DK, CG, CG, CG],
        [CG, CG, DK, DK, DK, DK, CG, CG],
        [CG, CG, CG, DK, DK, CG, CG, CG],
        [CG, CG, CG, CG, CG, CG, CG, CG],
        [N,  CG, CG, CG, CG, CG, CG, N ],
        [CG, CG, CG, CG, CG, CG, CG, CG],
        [CG, CG, CG, CG, CG, CG, CG, CG],
        [CG, CG, CG, CG, CG, CG, CG, CG],
        [N,  CG, CG, N,  N,  CG, CG, N ],
        [N,  CG, CG, N,  N,  CG, CG, N ],
        [N,  CG, CG, N,  N,  CG, CG, N ],
        [N,  CG, CG, N,  N,  CG, CG, N ],
    ],
    "zombie": [
        [N,  ZG, ZG, ZG, ZG, ZG, ZG, N ],
        [ZG, ZG, ZG, ZG, ZG, ZG, ZG, ZG],
        [ZG, DK, ZG, ZG, ZG, ZG, DK, ZG],
        [ZG, DK, ZG, ZG, ZG, ZG, DK, ZG],
        [ZG, ZG, ZG, ZG, ZG, ZG, ZG, ZG],
        [ZG, ZG, ZG, ZG, ZG, ZG, ZG, ZG],
        [ZG, CY, CY, CY, CY, CY, CY, ZG],
        [ZG, CY, CY, CY, CY, CY, CY, ZG],
        [ZG, CY, CY, CY, CY, CY, CY, ZG],
        [ZG, CY, CY, CY, CY, CY, CY, ZG],
        [ZG, CY, CY, CY, CY, CY, CY, ZG],
        [ZG, CY, CY, CY, CY, CY, CY, ZG],
        [N,  JE, JE, N,  N,  JE, JE, N ],
        [N,  JE, JE, N,  N,  JE, JE, N ],
        [N,  JE, JE, N,  N,  JE, JE, N ],
        [N,  JE, JE, N,  N,  JE, JE, N ],
    ],
    "skeleton": [
        [N,  BO, BO, BO, BO, BO, BO, N ],
        [BO, BO, BO, BO, BO, BO, BO, BO],
        [BO, DK, DK, BO, BO, DK, DK, BO],
        [BO, DK, DK, BO, BO, DK, DK, BO],
        [BO, BO, BO, BO, BO, BO, BO, BO],
        [BO, BO, DK, BO, BO, DK, BO, BO],
        [N,  N,  BO, N,  N,  BO, N,  N ],
        [N,  BO, BO, BO, BO, BO, BO, N ],
        [N,  N,  BO, N,  N,  BO, N,  N ],
        [N,  BO, BO, BO, BO, BO, BO, N ],
        [N,  N,  BO, N,  N,  BO, N,  N ],
        [N,  N,  BO, N,  N,  BO, N,  N ],
        [N,  N,  BO, N,  N,  BO, N,  N ],
        [N,  N,  BO, N,  N,  BO, N,  N ],
        [N,  N,  BO, N,  N,  BO, N,  N ],
        [N,  N,  BO, N,  N,  BO, N,  N ],
    ],
    "enderman": [
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  EK, EK, EK, EK, EK, EK, N ],
        [N,  EK, PU, EK, EK, PU, EK, N ],
        [N,  EK, PU, EK, EK, PU, EK, N ],
        [N,  EK, EK, EK, EK, EK, EK, N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [N,  N,  EK, EK, EK, EK, N,  N ],
        [EK, N,  EK, N,  N,  EK, N,  EK],
        [EK, N,  EK, N,  N,  EK, N,  EK],
        [EK, N,  EK, N,  N,  EK, N,  EK],
        [EK, N,  EK, N,  N,  EK, N,  EK],
        [N,  N,  EK, N,  N,  EK, N,  N ],
        [N,  N,  EK, N,  N,  EK, N,  N ],
        [N,  N,  EK, N,  N,  EK, N,  N ],
    ],
    "villager": [
        [N,  VL, VL, VL, VL, VL, VL, N ],
        [VL, VL, VL, VL, VL, VL, VL, VL],
        [VL, DK, VL, VL, VL, VL, DK, VL],
        [VL, DK, VL, VL, VL, VL, DK, VL],
        [VL, VL, VL, DK, DK, VL, VL, VL],
        [VL, VL, VL, VL, VL, VL, VL, VL],
        [N,  VR, VR, VR, VR, VR, VR, N ],
        [VR, VR, VR, VR, VR, VR, VR, VR],
        [VR, VR, VR, VR, VR, VR, VR, VR],
        [VR, VR, VR, VR, VR, VR, VR, VR],
        [VR, VR, VR, VR, VR, VR, VR, VR],
        [VR, VR, VR, VR, VR, VR, VR, VR],
        [N,  VR, VR, N,  N,  VR, VR, N ],
        [N,  VR, VR, N,  N,  VR, VR, N ],
        [N,  VL, VL, N,  N,  VL, VL, N ],
        [N,  VL, VL, N,  N,  VL, VL, N ],
    ],
    "pig": [
        [N,  PK, PK, PK, PK, PK, PK, N ],
        [PK, PK, PK, PK, PK, PK, PK, PK],
        [PK, DK, PK, PK, PK, PK, DK, PK],
        [PK, PK, RD, PK, PK, RD, PK, PK],
        [PK, PK, PK, PK, PK, PK, PK, PK],
        [PK, PK, PK, PK, PK, PK, PK, PK],
        [N,  PK, N,  PK, PK, N,  PK, N ],
        [N,  PK, N,  PK, PK, N,  PK, N ],
    ],
    "cow": [
        [N,  BR, BR, BR, BR, BR, BR, N ],
        [BR, WH, BR, BR, BR, BR, WH, BR],
        [BR, DK, BR, BR, BR, BR, DK, BR],
        [BR, BR, BR, BR, BR, BR, BR, BR],
        [WH, BR, WH, BR, BR, WH, BR, WH],
        [BR, BR, BR, BR, BR, BR, BR, BR],
        [N,  BR, N,  BR, BR, N,  BR, N ],
        [N,  BR, N,  BR, BR, N,  BR, N ],
    ],
    "chicken": [
        [N,  N,  N,  WH, WH, N,  N,  N ],
        [N,  RD, WH, WH, WH, YL, N,  N ],
        [N,  N,  WH, WH, WH, WH, N,  N ],
        [N,  WH, WH, WH, WH, WH, WH, N ],
        [N,  WH, WH, WH, WH, WH, WH, N ],
        [N,  N,  YL, N,  N,  YL, N,  N ],
    ],
    "spider": [
        [DK, N,  N,  DK, DK, N,  N,  DK],
        [DK, N,  DK, DK, DK, DK, N,  DK],
        [N,  DK, DK, RD, RD, DK, DK, N ],
        [N,  DK, RD, DK, DK, RD, DK, N ],
        [N,  DK, DK, DK, DK, DK, DK, N ],
        [DK, N,  DK, DK, DK, DK, N,  DK],
        [DK, N,  N,  DK, DK, N,  N,  DK],
    ],
}

# ── Biome-appropriate mob pools ───────────────────────────────────────────────
PASSIVE_MOBS = {
    "forest": ["pig", "cow", "chicken", "villager", "steve"],
    "desert": ["steve", "villager"],
    "snow":   ["chicken", "steve"],
    "plains": ["pig", "cow", "chicken", "villager", "steve"],
    "jungle": ["pig", "chicken", "steve"],
}

HOSTILE_MOBS = {
    "forest": ["creeper", "zombie"],
    "desert": ["skeleton", "creeper"],
    "snow":   ["zombie", "skeleton"],
    "plains": ["creeper", "zombie"],
    "jungle": ["creeper", "spider"],
}


# ── Terrain helpers ───────────────────────────────────────────────────────────
def smooth(arr, n=3):
    for _ in range(n):
        s = list(arr)
        for i in range(1, len(arr) - 1):
            s[i] = (arr[i-1] + arr[i] + arr[i+1]) / 3
        arr = s
    return [int(v) for v in arr]


def gen_heightmap(width, base, var):
    lo, hi = base - var * 3, base + var * 3
    h = [base]
    for _ in range(width - 1):
        h.append(max(lo, min(hi, h[-1] + random.randint(-var, var))))
    return smooth(h)


# ── Block drawing helpers ─────────────────────────────────────────────────────
def draw_block(px, bx, by, color):
    x0, y0 = bx * BLOCK, by * BLOCK
    dark = tuple(max(0, c - 32) for c in color)
    for dy in range(BLOCK):
        for dx in range(BLOCK):
            px[x0 + dx, y0 + dy] = dark if (dx == 0 or dy == 0) else color


def draw_ore(px, bx, by, ore):
    draw_block(px, bx, by, PALETTE[STONE])
    spot = ORE_SPOTS[ore]
    x0, y0 = bx * BLOCK, by * BLOCK
    for sx, sy in [(2, 2), (2, 5), (5, 2), (4, 6), (6, 4), (1, 4), (3, 1)]:
        if random.random() < 0.55 and sx < BLOCK and sy < BLOCK:
            px[x0 + sx, y0 + sy] = spot
            if sx + 1 < BLOCK:
                px[x0 + sx + 1, y0 + sy] = spot


def draw_sprite(px, sprite, cx_px, surface_py):
    """Draw a sprite centred at cx_px, feet at surface_py (native pixels)."""
    rows = len(sprite)
    cols = len(sprite[0])
    base_x = cx_px - (cols * SP) // 2
    base_y = surface_py - rows * SP
    for row_i, row in enumerate(sprite):
        for col_i, color in enumerate(row):
            if color is None:
                continue
            for dy in range(SP):
                for dx in range(SP):
                    nx = base_x + col_i * SP + dx
                    ny = base_y + row_i * SP + dy
                    if 0 <= nx < W * BLOCK and 0 <= ny < H * BLOCK:
                        px[nx, ny] = color


# ── Building placement ────────────────────────────────────────────────────────
def place_house(world, heights, cx):
    """Wooden house (planks walls, oak log peaked roof)."""
    hw = 4
    hc = heights[cx]
    # Walls: 2 blocks tall at each column's local height
    for x in range(max(0, cx - hw), min(W, cx + hw + 1)):
        h = heights[x]
        for y_off in [1, 2]:
            if h - y_off >= 0:
                world[x][h - y_off] = PLANKS
    # Peaked roof: 3 narrowing layers above hc-2
    for layer, half in enumerate([hw, hw - 1, hw - 2]):
        ry = hc - 3 - layer
        if ry < 0:
            break
        for x in range(max(0, cx - half), min(W, cx + half + 1)):
            if world[x][ry] == AIR:
                world[x][ry] = OAK_LOG
    # Windows
    for wx in [cx - 2, cx + 2]:
        if 0 <= wx < W and heights[wx] - 2 >= 0:
            world[wx][heights[wx] - 2] = GLASS
    # Door gap
    if 0 <= cx < W and heights[cx] - 1 >= 0:
        world[cx][heights[cx] - 1] = AIR


def place_temple(world, heights, cx):
    """Sandstone pyramid for desert."""
    hw = 5
    hc = heights[cx]
    for layer in range(hw + 1):
        ry = hc - 1 - layer
        if ry < 0:
            break
        half = hw - layer
        for x in range(max(0, cx - half), min(W, cx + half + 1)):
            if world[x][ry] in (AIR, SAND):
                world[x][ry] = SANDSTONE


def place_cabin(world, heights, cx):
    """Spruce-log cabin for snow biome."""
    hw = 3
    hc = heights[cx]
    for x in range(max(0, cx - hw), min(W, cx + hw + 1)):
        h = heights[x]
        for y_off in [1, 2]:
            if h - y_off >= 0:
                world[x][h - y_off] = SPRUCE_LOG
    # Snow-cap roof
    for layer, half in enumerate([hw, hw - 1, 0]):
        ry = hc - 3 - layer
        if ry < 0:
            break
        for x in range(max(0, cx - half), min(W, cx + half + 1)):
            if world[x][ry] == AIR:
                world[x][ry] = SNOW
    # Door
    if 0 <= cx < W and heights[cx] - 1 >= 0:
        world[cx][heights[cx] - 1] = AIR


def place_jungle_temple(world, heights, cx):
    """Crumbling cobblestone ruin for jungle."""
    hw = 3
    hc = heights[cx]
    # Hollow outer walls
    for x in range(max(0, cx - hw), min(W, cx + hw + 1)):
        is_edge = (x == cx - hw or x == cx + hw)
        h = heights[x]
        for y_off in [1, 2, 3]:
            wy = h - y_off
            if wy < 0:
                continue
            if is_edge or y_off == 3:
                world[x][wy] = COBBLE
    # Flat roof
    ry = hc - 4
    if ry >= 0:
        for x in range(max(0, cx - hw), min(W, cx + hw + 1)):
            if world[x][ry] == AIR:
                world[x][ry] = COBBLE
    # Entrance
    if 0 <= cx < W:
        h = heights[cx]
        for y_off in [1, 2]:
            if h - y_off >= 0:
                world[cx][h - y_off] = AIR


def place_castle(world, heights, cx):
    """Very large stone castle: twin towers (12 tall), curtain walls (5 tall), central keep (9 tall)."""
    hc = heights[cx]

    def fill(x1, x2, h_blocks):
        for x in range(max(0, x1), min(W, x2 + 1)):
            h = heights[x]
            for y in range(max(0, hc - h_blocks), min(H - 1, max(hc, h) + 1)):
                world[x][y] = COBBLE

    def battlements(x1, x2, h_blocks):
        y = hc - h_blocks - 1
        if y < 0:
            return
        for x in range(max(0, x1), min(W, x2 + 1)):
            if x % 2 == 0 and 0 <= x < W and world[x][y] == AIR:
                world[x][y] = COBBLE

    # Left tower
    fill(cx - 12, cx - 9, 12)
    battlements(cx - 12, cx - 9, 12)
    for y_off in [4, 8]:
        wy = hc - y_off
        if wy >= 0:
            for wx in [cx - 11, cx - 10]:
                if 0 <= wx < W:
                    world[wx][wy] = GLASS

    # Right tower
    fill(cx + 9, cx + 12, 12)
    battlements(cx + 9, cx + 12, 12)
    for y_off in [4, 8]:
        wy = hc - y_off
        if wy >= 0:
            for wx in [cx + 10, cx + 11]:
                if 0 <= wx < W:
                    world[wx][wy] = GLASS

    # Left curtain wall
    fill(cx - 8, cx - 5, 5)
    battlements(cx - 8, cx - 5, 5)

    # Right curtain wall
    fill(cx + 5, cx + 8, 5)
    battlements(cx + 5, cx + 8, 5)

    # Central keep: solid walls, hollow interior
    for x in range(max(0, cx - 4), min(W, cx + 5)):
        is_wall = (x == cx - 4 or x == cx + 4)
        for y_off in range(1, 10):
            wy = hc - y_off
            if wy < 0:
                continue
            if is_wall:
                world[x][wy] = COBBLE
            elif y_off == 1:
                world[x][wy] = STONE
    # Keep roof + battlements
    if hc - 10 >= 0:
        for x in range(max(0, cx - 4), min(W, cx + 5)):
            world[x][hc - 10] = COBBLE
    if hc - 11 >= 0:
        for x in range(max(0, cx - 4), min(W, cx + 5)):
            if x % 2 == 0 and world[x][hc - 11] == AIR:
                world[x][hc - 11] = COBBLE
    # Keep windows
    for y_off in [3, 6]:
        wy = hc - y_off
        if wy >= 0:
            for wx in [cx - 3, cx, cx + 3]:
                if 0 <= wx < W:
                    world[wx][wy] = GLASS
    # Gate entrance
    for gx in range(max(0, cx - 1), min(W, cx + 2)):
        for y_off in [1, 2]:
            wy = hc - y_off
            if wy >= 0:
                world[gx][wy] = AIR
    if hc - 3 >= 0:
        for gx in range(max(0, cx - 1), min(W, cx + 2)):
            if world[gx][hc - 3] == COBBLE:
                world[gx][hc - 3] = PLANKS


def place_watchtower(world, heights, cx):
    """Tall cobblestone watchtower with battlements and windows."""
    hc = heights[cx]
    hw = 2
    tower_h = 11
    for x in range(max(0, cx - hw), min(W, cx + hw + 1)):
        h = heights[x]
        for y in range(max(0, hc - tower_h), min(H - 1, max(hc, h) + 1)):
            world[x][y] = COBBLE
    batt_y = hc - tower_h - 1
    if batt_y >= 0:
        for x in range(max(0, cx - hw), min(W, cx + hw + 1)):
            if x % 2 == 0 and world[x][batt_y] == AIR:
                world[x][batt_y] = COBBLE
    for y_off in [4, 7]:
        wy = hc - y_off
        if wy >= 0 and 0 <= cx < W:
            world[cx][wy] = GLASS
    if hc - 1 >= 0 and 0 <= cx < W:
        world[cx][hc - 1] = AIR


def place_barn(world, heights, cx):
    """Large wooden barn with gambrel roof and wide door."""
    hc = heights[cx]
    hw = 6
    wall_h = 4
    for x in range(max(0, cx - hw), min(W, cx + hw + 1)):
        h = heights[x]
        is_corner = (x == cx - hw or x == cx + hw)
        for y_off in range(1, wall_h + 1):
            wy = hc - y_off
            if wy >= 0:
                world[x][wy] = OAK_LOG if is_corner else PLANKS
        for y in range(hc + 1, min(H - 1, h + 1)):
            world[x][y] = OAK_LOG if is_corner else PLANKS
    for i, half in enumerate([hw, hw - 2, hw - 4, hw - 5]):
        if half < 0:
            break
        ry = hc - wall_h - 1 - i
        if ry < 0:
            break
        for x in range(max(0, cx - half), min(W, cx + half + 1)):
            if world[x][ry] == AIR:
                world[x][ry] = OAK_LOG
    for gx in range(max(0, cx - 1), min(W, cx + 2)):
        for y_off in [1, 2, 3]:
            wy = hc - y_off
            if wy >= 0:
                world[gx][wy] = AIR
    for wx in [cx - hw + 2, cx + hw - 2]:
        if 0 <= wx < W:
            wy = hc - wall_h
            if wy >= 0:
                world[wx][wy] = GLASS


def place_lighthouse(world, heights, cx):
    """Tall lighthouse with a wide base, narrow shaft, glass lamp room, and striped walls."""
    hc = heights[cx]
    for y_off in range(1, 7):
        wy = hc - y_off
        if wy >= 0:
            for x in range(max(0, cx - 2), min(W, cx + 3)):
                world[x][wy] = COBBLE
    for y_off in range(7, 15):
        wy = hc - y_off
        if wy >= 0:
            for x in range(max(0, cx - 1), min(W, cx + 2)):
                world[x][wy] = COBBLE if y_off % 3 != 0 else PLANKS
    for y_off in range(15, 17):
        wy = hc - y_off
        if wy >= 0:
            for x in range(max(0, cx - 1), min(W, cx + 2)):
                world[x][wy] = GLASS
    if hc - 17 >= 0:
        for x in range(max(0, cx - 1), min(W, cx + 2)):
            world[x][hc - 17] = COBBLE
    if hc - 7 >= 0:
        for x in range(max(0, cx - 2), min(W, cx + 3)):
            if world[x][hc - 7] == AIR:
                world[x][hc - 7] = COBBLE
    if hc - 1 >= 0 and 0 <= cx < W:
        world[cx][hc - 1] = AIR
    for x in range(max(0, cx - 2), min(W, cx + 3)):
        h = heights[x]
        for y in range(hc + 1, min(H - 1, h + 1)):
            world[x][y] = COBBLE


STRUCTURES = {
    "castle":     place_castle,
    "watchtower": place_watchtower,
    "barn":       place_barn,
    "lighthouse": place_lighthouse,
}


# ── World building ────────────────────────────────────────────────────────────
# ── Renderer ──────────────────────────────────────────────────────────────────
def render(world, heights, biome, tod, sky_objs, entities):
    img = Image.new("RGB", (W * BLOCK, H * BLOCK), SKY_COLORS[tod])
    px  = img.load()

    # ── blocks ──
    water_color = PALETTE[WATER]
    sky_color   = SKY_COLORS[tod]
    for bx in range(W):
        for by in range(H):
            blk = world[bx][by]
            if blk == AIR:
                continue
            elif blk in ORE_SPOTS:
                draw_ore(px, bx, by, blk)
            elif blk == WATER:
                blend = tuple(int(sky_color[i] * 0.25 + water_color[i] * 0.75) for i in range(3))
                draw_block(px, bx, by, blend)
            elif blk in PALETTE:
                draw_block(px, bx, by, PALETTE[blk])

    # ── stars (night) ──
    if tod == "night":
        min_surf_y = min(heights) * BLOCK
        for _ in range(110):
            sx = random.randint(0, W * BLOCK - 1)
            sy = random.randint(0, max(1, min_surf_y - BLOCK) - 1)
            b  = random.randint(160, 240)
            px[sx, sy] = (b, b, min(255, b + 20))

    # ── sun / moon / clouds ──
    for etype, ex, ey, size in sky_objs:
        x0, y0 = ex * BLOCK, ey * BLOCK
        if etype == "sun":
            for dy in range(3 * BLOCK):
                for dx in range(3 * BLOCK):
                    nx, ny = x0 + dx, y0 + dy
                    if 0 <= nx < W * BLOCK and 0 <= ny < H * BLOCK:
                        px[nx, ny] = (255, 218, 46)
        elif etype == "moon":
            for dy in range(2 * BLOCK):
                for dx in range(2 * BLOCK):
                    nx, ny = x0 + dx, y0 + dy
                    if 0 <= nx < W * BLOCK and 0 <= ny < H * BLOCK:
                        px[nx, ny] = (218, 220, 198)
        elif etype == "cloud":
            for dy in range(2 * BLOCK):
                for dx in range(size * BLOCK):
                    nx, ny = x0 + dx, y0 + dy
                    if dy < BLOCK or (dx % (BLOCK * 2)) < BLOCK + 4:
                        if 0 <= nx < W * BLOCK and 0 <= ny < H * BLOCK:
                            px[nx, ny] = (242, 244, 248)

    # ── entities (drawn on top of everything) ──
    for sprite_key, cx_px, surface_py in entities:
        draw_sprite(px, SPRITES[sprite_key], cx_px, surface_py)

    return img


# ── World building (parameterised) ───────────────────────────────────────────
def build_world_with_params(biome=None, tod=None, forced_entities=None):
    """Like build_world() but accepts optional overrides from the web UI."""
    if biome is None:
        biome = random.choice(BIOMES)
    if tod is None:
        tod = random.choice(TIMES)

    var     = {"forest": 4, "desert": 2, "snow": 4, "plains": 2, "jungle": 3}[biome]
    base    = 32
    heights = gen_heightmap(W, base, var)
    water_y = base + 2

    world = [[AIR] * H for _ in range(W)]

    # ── terrain fill ──
    for x in range(W):
        h = heights[x]
        for y in range(h, H):
            depth = y - h
            if y >= H - 2:
                world[x][y] = BEDROCK
            elif biome == "desert":
                world[x][y] = SAND if depth < 5 else (SANDSTONE if depth < 8 else STONE)
            elif biome == "snow":
                world[x][y] = SNOW if depth == 0 else (DIRT if depth < 4 else STONE)
            else:
                world[x][y] = GRASS if depth == 0 else (DIRT if depth < 4 else STONE)

    # ── water ──
    if biome != "desert":
        for x in range(W):
            if heights[x] > water_y:
                for y in range(water_y, heights[x]):
                    if world[x][y] == AIR:
                        world[x][y] = WATER

    # ── ores ──
    for x in range(W):
        for y in range(H):
            if world[x][y] != STONE:
                continue
            r = random.random()
            if   y > H - 8  and r < 0.07: world[x][y] = DIAMOND
            elif y > H - 15 and r < 0.05: world[x][y] = GOLD
            elif r < 0.08:                 world[x][y] = IRON
            elif r < 0.13:                 world[x][y] = COAL

    # ── caves ──
    for _ in range(random.randint(3, 7)):
        cx  = random.randint(3, W - 4)
        cy  = random.randint(min(heights) + 6, H - 6)
        vx  = random.choice([-1, 0, 1])
        vy  = random.choice([-1, 0, 1])
        for _ in range(random.randint(6, 18)):
            if 1 < cx < W - 2 and 1 < cy < H - 3:
                if world[cx][cy] not in (AIR, WATER, LAVA, BEDROCK):
                    world[cx][cy] = AIR
            if random.random() < 0.35:
                vx, vy = random.choice([-1, 0, 1]), random.choice([-1, 0, 1])
            cx = max(1, min(W - 2, cx + vx))
            cy = max(min(heights) + 4, min(H - 4, cy + vy))

    # ── lava at cave floors ──
    for x in range(W):
        for y in range(H - 5, H - 2):
            if world[x][y] == AIR:
                world[x][y] = LAVA

    # ── buildings ──
    forced_structs = [e for e in (forced_entities or []) if e in STRUCTURES]
    if forced_structs:
        struct_xs = []
        for name in forced_structs:
            margin = 14 if name == "castle" else 10
            for _ in range(30):
                bx = random.randint(margin, W - margin - 1)
                if not any(abs(bx - ox) < 18 for ox in struct_xs):
                    struct_xs.append(bx)
                    STRUCTURES[name](world, heights, bx)
                    break
    else:
        num_buildings = random.randint(1, 2)
        building_xs = set()
        for _ in range(num_buildings):
            bx = random.randint(12, W - 14)
            if any(abs(bx - ox) < 12 for ox in building_xs):
                continue
            building_xs.add(bx)
            if biome == "desert":
                place_temple(world, heights, bx)
            elif biome == "snow":
                place_cabin(world, heights, bx)
            elif biome == "jungle":
                place_jungle_temple(world, heights, bx)
            else:
                place_house(world, heights, bx)

    # ── trees / cacti ──
    th_min, th_max, log, leaves, shape, target = TREE_PARAMS[biome]
    placed, tries = 0, 0
    surf = SURF_BLOCK[biome]

    while placed < target and tries < W * 5:
        tries += 1
        x = random.randint(2, W - 4)
        h = heights[x]
        if world[x][h] != surf:
            continue
        if shape == "cactus":
            ch = random.randint(2, 4)
            if any(h - i - 1 < 0 or h - i - 1 >= H for i in range(ch)):
                continue
            if ((x > 0   and world[x-1][h-1] != AIR) or
                    (x < W-1 and world[x+1][h-1] != AIR)):
                continue
            for i in range(ch):
                world[x][h - i - 1] = CACTUS
            placed += 1
        else:
            th    = random.randint(th_min, th_max)
            top_y = h - th
            if top_y < 2:
                continue
            for y in range(top_y, h):
                world[x][y] = log
            if shape == "triangular":
                for i, y in enumerate(range(top_y, top_y + th // 2 + 2)):
                    spread = i // 2
                    for lx in range(x - spread, x + spread + 1):
                        if 0 <= lx < W and 0 <= y < H and world[lx][y] == AIR:
                            world[lx][y] = leaves
            else:
                for y in range(top_y - 1, top_y + 3):
                    for lx in range(x - 2, x + 3):
                        if 0 <= lx < W and 0 <= y < H and world[lx][y] == AIR:
                            world[lx][y] = leaves
            placed += 1

    # ── entity placement ──
    if forced_entities:
        pool = [e for e in forced_entities if e in SPRITES]
    elif tod == "night":
        pool = list(HOSTILE_MOBS.get(biome, ["zombie", "creeper"]))
        pool.append("enderman")
    else:
        pool = list(PASSIVE_MOBS.get(biome, ["steve", "pig"]))
        if random.random() < 0.25:
            hostile = HOSTILE_MOBS.get(biome, ["creeper"])
            pool.append(random.choice(hostile))

    pool = [s for s in pool if s in SPRITES]
    if not pool:
        pool = ["steve"]

    entities = []
    num_entities = random.randint(3, 7)
    entity_tries = 0

    while len(entities) < num_entities and entity_tries < W * 4:
        entity_tries += 1
        x = random.randint(2, W - 3)
        h = heights[x]
        if world[x][h] not in (GRASS, SAND, SNOW) or world[x][h-1] != AIR:
            continue
        if any(abs(x * BLOCK - e[1]) < 12 for e in entities):
            continue
        sprite_key = random.choice(pool)
        cx_px     = x * BLOCK + BLOCK // 2
        surface_py = h * BLOCK
        entities.append((sprite_key, cx_px, surface_py))

    # ── sky objects ──
    sky_objs = []
    if tod == "night":
        sky_objs.append(("moon", random.randint(5, W - 8), random.randint(1, 3), 2))
    else:
        sky_objs.append(("sun",  random.randint(5, W - 10), random.randint(1, 4), 3))
    for _ in range(random.randint(2, 5)):
        sky_objs.append(("cloud", random.randint(0, W - 9),
                          random.randint(1, 6), random.randint(4, 9)))

    return world, heights, biome, tod, sky_objs, entities


# ── Legacy build_world kept for compatibility ─────────────────────────────────
def build_world():
    return build_world_with_params()


# ── Shared scene-save helper ──────────────────────────────────────────────────
def generate_scene(biome=None, tod=None, forced_entities=None, scale=3, open_file=False):
    """Generate a scene and return (PIL Image, path, biome, tod, mobs_str)."""
    world, heights, biome, tod, sky_objs, entities = build_world_with_params(
        biome=biome, tod=tod, forced_entities=forced_entities
    )
    img = render(world, heights, biome, tod, sky_objs, entities)

    w, h = img.size
    img  = img.resize((w * scale, h * scale), Image.NEAREST)

    draw  = ImageDraw.Draw(img)
    sprite_names = {e[0] for e in entities}
    struct_names = {e for e in (forced_entities or []) if e in STRUCTURES}
    mobs  = ", ".join(sorted(sprite_names | struct_names)) or "none"
    label = f"  Biome: {biome.upper()}   |   {tod.upper()}   |   {mobs}  "
    try:
        bbox = draw.textbbox((0, 0), label)
        tw   = bbox[2] - bbox[0]
    except AttributeError:
        tw = len(label) * 7
    draw.rectangle([8, 8, tw + 14, 30], fill=(0, 0, 0))
    draw.text((12, 10), label, fill=(255, 255, 255))

    out_dir = "/tmp/minecraft_scenes"
    os.makedirs(out_dir, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"scene_{biome}_{tod}_{ts}.png")
    img.save(path)

    if open_file:
        subprocess.run(["open", path], check=False)

    return img, path, biome, tod, mobs


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    img, path, biome, tod, mobs = generate_scene(open_file=True)
    print(f"Saved → {path}")
    print(f"Biome: {biome}  |  Time: {tod}  |  Entities: {mobs}")


if __name__ == "__main__":
    main()
