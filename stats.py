#!/usr/bin/env python3
"""Fetches GitHub stats and draws the pixel-art HUD. Usage: python3 stats.py [out.svg] (GITHUB_TOKEN or gh auth)."""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

from pixel import Canvas, P

LOGIN = os.environ.get("STATS_LOGIN", "SametGoktepe")
API = "https://api.github.com/graphql"
QUERY = """
query($login:String!,$from:DateTime!,$to:DateTime!,$after:String){
  user(login:$login){
    createdAt followers{totalCount} pullRequests{totalCount} issues{totalCount}
    repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100,after:$after){
      totalCount pageInfo{hasNextPage endCursor} nodes{stargazerCount}}
    contributionsCollection(from:$from,to:$to){
      totalCommitContributions restrictedContributionsCount
      contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
  }
}"""
ICONS = {
    "grid": ["########", "#......#", "#.#.#.##", "#......#", "#.#.#.##", "#......#", "#.#.#.##", "########"],
    "flame": ["...##...", "..###...", "..####..", ".#####..", "#######.", "########", ".######.", "..####.."],
    "trophy": ["########", "#.####.#", "#.####.#", ".######.", "..####..", "...##...", "..####..", ".######."],
    "star": ["...##...", "...##...", "..####..", "########", ".######.", "..####..", ".##..##.", ".#....#."],
    "people": ["..####..", "..####..", "...##...", ".######.", "########", "########", ".##..##.", ".##..##."],
    "repo": ["########", "#......#", "#.####.#", "#.#....#", "#.####.#", "#......#", "#......#", "########"],
    "commit": ["...##...", "...##...", "..####..", ".##..##.", ".##..##.", "..####..", "...##...", "...##..."],
    "pr": ["##....##", "##....##", "##....##", "##....##", "##....##", ".##..##.", "..####..", "...##..."],
    "issue": ["..####..", ".#....#.", "#......#", "#..##..#", "#..##..#", "#......#", ".#....#.", "..####.."],
}


def token():
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def gql(variables):
    try:
        return gql_http(variables)
    except urllib.error.URLError as err:
        if "CERTIFICATE_VERIFY_FAILED" not in str(err):
            raise
        return gql_gh(variables)  # local Python without CA certs: let gh do the request


def gql_http(variables):
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    req = urllib.request.Request(API, body, {"Authorization": f"bearer {token()}", "Content-Type": "application/json",
                                             "User-Agent": "profile-readme-stats"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return unwrap(json.load(resp))


def gql_gh(variables):
    cmd = ["gh", "api", "graphql", "-f", f"query={QUERY}"]
    for key, value in variables.items():
        if value is not None:
            cmd += ["-f", f"{key}={value}"]
    return unwrap(json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout))


def unwrap(data):
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch():
    now = dt.datetime.now(dt.timezone.utc)
    first = gql({"login": LOGIN, "from": iso(now - dt.timedelta(days=365)), "to": iso(now), "after": None})
    created = dt.datetime.fromisoformat(first["createdAt"].replace("Z", "+00:00"))
    stars, repos = sum(n["stargazerCount"] for n in first["repositories"]["nodes"]), first["repositories"]
    while repos["pageInfo"]["hasNextPage"]:
        repos = gql({"login": LOGIN, "from": iso(now - dt.timedelta(days=1)), "to": iso(now),
                     "after": repos["pageInfo"]["endCursor"]})["repositories"]
        stars += sum(n["stargazerCount"] for n in repos["nodes"])
    days, commits, total = {}, 0, 0
    for year in range(created.year, now.year + 1):
        start = max(created, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        end = min(now, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        coll = gql({"login": LOGIN, "from": iso(start), "to": iso(end), "after": None})["contributionsCollection"]
        # private-repo activity only surfaces as a restricted count; it is overwhelmingly commits here
        commits += coll["totalCommitContributions"] + coll["restrictedContributionsCount"]
        total += coll["contributionCalendar"]["totalContributions"]
        for week in coll["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                days[day["date"]] = day["contributionCount"]
    ordered = sorted(days)
    longest = run = 0
    for d in ordered:
        run = run + 1 if days[d] > 0 else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(ordered):
        if days[d] > 0:
            current += 1
        elif d != ordered[-1]:
            break
    return dict(year=first["contributionsCollection"]["contributionCalendar"]["totalContributions"], total=total,
                current=current, longest=longest, stars=stars, followers=first["followers"]["totalCount"],
                repos=first["repositories"]["totalCount"], commits=commits, prs=first["pullRequests"]["totalCount"],
                issues=first["issues"]["totalCount"], updated=now.strftime("%Y-%m-%d"))


def fmt(n):
    return f"{n:,}"


def render(s):
    W, H = 520, 118
    cv = Canvas(W, H)
    cv.fill(0, 0, W, H, P["steel"])
    cv.bevel(0, 0, W, H, P["steel_hi"], P["steel_lo"])
    cv.fill(6, 6, W - 12, H - 12, P["dusk"])
    cv.text(14, 12, "GITHUB STATS", P["cream"])
    right = cv.text_right(W - 14, 12, "LIVE", P["mute"]) - cv.text_width("LIVE") - 8
    cv.rect(right, 15, 3, 3, P["teal"], "live")
    cv.text_right(right - 10, 12, f'UPDATED {s["updated"]}', P["mute"])
    big = [("grid", "CONTRIBUTIONS", fmt(s["total"]), f'{fmt(s["year"])} IN THE LAST YEAR'),
           ("flame", "CURRENT STREAK", f'{s["current"]} DAYS', None),
           ("trophy", "LONGEST STREAK", f'{s["longest"]} DAYS', None)]
    for i, (icon, label, value, note) in enumerate(big):
        x, cell = 14 + i * 168, 160
        cv.sprite(x, 30, ICONS[icon], P["amber"])
        assert 12 + cv.text_width(label) <= cell and cv.text_width(value, 2) <= cell, label
        cv.text(x + 12, 30, label, P["mute"])
        cv.text(x, 42, value, P["cream"], 2)
        if note:
            assert cv.text_width(note) <= cell, note
            cv.text(x, 60, note, P["mute"])
    small = [("star", "STARS", s["stars"]), ("people", "FOLLOWERS", s["followers"]), ("repo", "REPOS", s["repos"]),
             ("commit", "COMMITS", s["commits"]), ("pr", "PRS", s["prs"]), ("issue", "ISSUES", s["issues"])]
    for i, (icon, label, value) in enumerate(small):
        x, cell = 14 + i * 82, 78
        assert cv.text_width(label) <= cell and 12 + cv.text_width(fmt(value)) <= cell, label
        cv.sprite(x, 78, ICONS[icon], P["teal"])
        cv.text(x + 12, 78, fmt(value), P["cream"])
        cv.text(x, 90, label, P["mute"])
    css = ".live{animation:blink 1.2s steps(1,end) infinite}@keyframes blink{50%{opacity:0}}"
    alt = (f'GitHub stats: {s["total"]} contributions all time ({s["year"]} in the last year), current streak '
           f'{s["current"]} days, longest streak {s["longest"]} days, {s["stars"]} stars, {s["followers"]} followers, '
           f'{s["repos"]} repos, {s["commits"]} commits, {s["prs"]} pull requests, {s["issues"]} issues.')
    return cv.svg(css, alt)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets/stats.svg"
    stats = fetch()
    print(json.dumps(stats))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(render(stats))
    print("written", out)
