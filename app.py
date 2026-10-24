import random
from collections import deque

import streamlit as st

st.set_page_config(page_title="수달 미로찾기", page_icon="🦦", layout="centered")

WALL, PATH = 1, 0
OTTER, FISH, TRAIL, HINT = "🦦", "🐟", "🫧", "✨"


# ---------- 미로 생성 / 탐색 ----------
def generate_maze(n: int):
    """n x n 칸짜리 미로를 DFS로 생성. 실제 격자는 (2n+1) x (2n+1)."""
    size = 2 * n + 1
    grid = [[WALL] * size for _ in range(size)]
    stack = [(1, 1)]
    grid[1][1] = PATH
    while stack:
        r, c = stack[-1]
        nbrs = [
            (r + dr, c + dc, dr, dc)
            for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2))
            if 0 < r + dr < size - 1 and 0 < c + dc < size - 1
            and grid[r + dr][c + dc] == WALL
        ]
        if nbrs:
            nr, nc, dr, dc = random.choice(nbrs)
            grid[r + dr // 2][c + dc // 2] = PATH
            grid[nr][nc] = PATH
            stack.append((nr, nc))
        else:
            stack.pop()
    return grid


def bfs(grid, start):
    """start에서 모든 칸까지의 최단 거리와 이전 칸 정보를 반환."""
    dist = {start: 0}
    prev = {}
    q = deque([start])
    while q:
        r, c = q.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if grid[nr][nc] == PATH and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                prev[(nr, nc)] = (r, c)
                q.append((nr, nc))
    return dist, prev


def shortest_path(grid, start, goal):
    _, prev = bfs(grid, start)
    path, cur = [], goal
    while cur != start:
        path.append(cur)
        cur = prev[cur]
    return path


def new_game(n: int):
    grid = generate_maze(n)
    start = (1, 1)
    dist, _ = bfs(grid, start)
    goal = max(dist, key=dist.get)  # 시작점에서 가장 먼 곳에 생선 배치
    st.session_state.update(
        grid=grid, pos=start, start=start, goal=goal,
        moves=0, trail={start}, won=False, n=n,
    )


# ---------- 이동 ----------
def move(dr, dc):
    s = st.session_state
    if s.won:
        return
    r, c = s.pos
    nr, nc = r + dr, c + dc
    if s.grid[nr][nc] == PATH:
        s.pos = (nr, nc)
        s.moves += 1
        s.trail.add((nr, nc))
        if s.pos == s.goal:
            s.won = True


# ---------- 렌더링 ----------
def render(show_hint: bool):
    s = st.session_state
    grid, pos, goal = s.grid, s.pos, s.goal
    size = len(grid)
    px = max(14, min(32, 560 // size))
    hint = set(shortest_path(grid, pos, goal)) if show_hint and not s.won else set()

    rows = []
    for r in range(size):
        cells = []
        for c in range(size):
            if (r, c) == pos:
                bg, ch = "#9fd8f0", OTTER
            elif (r, c) == goal:
                bg, ch = "#9fd8f0", FISH
            elif grid[r][c] == WALL:
                bg, ch = "#2f6b4f", ""   # 갈대숲/바위
            elif (r, c) in hint:
                bg, ch = "#d9f2ff", HINT
            elif (r, c) in s.trail:
                bg, ch = "#bfe6f7", TRAIL
            else:
                bg, ch = "#9fd8f0", ""   # 호수 물길
            cells.append(
                f'<td style="width:{px}px;height:{px}px;background:{bg};'
                f'text-align:center;font-size:{int(px*0.7)}px;'
                f'line-height:{px}px;padding:0;">{ch}</td>'
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")

    html = (
        '<div style="display:flex;justify-content:center;">'
        '<table style="border-collapse:collapse;border:4px solid #1d4a37;'
        'border-radius:6px;table-layout:fixed;">'
        + "".join(rows) + "</table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------- UI ----------
st.title("🦦 수달의 호수 미로")
st.caption("수달을 움직여서 호수 끝에 있는 생선 🐟 을 찾아 먹으세요!")

if "grid" not in st.session_state:
    new_game(7)

with st.sidebar:
    st.header("설정")
    level = st.slider("미로 크기", 4, 15, st.session_state.n)
    show_hint = st.checkbox("✨ 힌트 보기 (최단 경로)")
    if st.button("🔄 새 미로 만들기", use_container_width=True):
        new_game(level)
        st.rerun()

s = st.session_state
c1, c2 = st.columns(2)
c1.metric("이동 횟수", s.moves)
c2.metric("최단 거리", len(shortest_path(s.grid, s.start, s.goal)))

render(show_hint)

if s.won:
    st.balloons()
    best = len(shortest_path(s.grid, s.start, s.goal))
    st.success(f"🎉 생선을 먹었어요! {s.moves}번 만에 도착 (최단 {best}번)")

st.write("")
_, up, _ = st.columns([1, 1, 1])
left, down, right = st.columns(3)
up.button("⬆️", on_click=move, args=(-1, 0), use_container_width=True)
left.button("⬅️", on_click=move, args=(0, -1), use_container_width=True)
down.button("⬇️", on_click=move, args=(1, 0), use_container_width=True)
right.button("➡️", on_click=move, args=(0, 1), use_container_width=True)
