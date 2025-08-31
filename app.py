from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get")
def get_json_data():
    url = "https://www.pcso.gov.ph/SearchLottoResult.aspx"
    request_headers = {
        "authority": "www.pcso.gov.ph",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "ASP.NET_SessionId=zf00tjihonx53014yvlmrwgy; AWSALBTG=aBM9dlabz+eAWxz/IGfVz02l+n+SB0oW+PRboUB84/3pv6fw52N0b//VptnVBgDei3h6gwBHDMufsIKSZxJU1QcVX67mgd9o/2YXAGbggZDhL/ft3Kicb2lnZXOEcTysIhKSzHvyX8Wjmsn2mnwZvbDJMiGth5TPGhX2IMmBXWRy; AWSALBTGCORS=aBM9dlabz+eAWxz/IGfVz02l+n+SB0oW+PRboUB84/3pv6fw52N0b//VptnVBgDei3h6gwBHDMufsIKSZxJU1QcVX67mgd9o/2YXAGbggZDhL/ft3Kicb2lnZXOEcTysIhKSzHvyX8Wjmsn2mnwZvbDJMiGth5TPGhX2IMmBXWRy; AWSALB=jLx0SrBkJhP9VRso9l3w9HlO9IDxjJ6M9PMJmqxTKgLIJz3KBsZ/5whd3RFDMJ8AvHWnayo29GMu/WV1Ge1EYY8JTZgTzSQF2qAffUanmdONN+zqSvH7E0RyykX4; AWSALBCORS=jLx0SrBkJhP9VRso9l3w9HlO9IDxjJ6M9PMJmqxTKgLIJz3KBsZ/5whd3RFDMJ8AvHWnayo29GMu/WV1Ge1EYY8JTZgTzSQF2qAffUanmdONN+zqSvH7E0RyykX4",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=request_headers, timeout=10)

        if response.status_code == 403:
            return JSONResponse(
                content={
                    "error": "Access Denied by the server",
                    "status_code": 403,
                    "response_headers": dict(response.headers)
                },
                status_code=403
            )

        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table
        table = soup.find('table', {'id': 'cphContainer_cpContent_GridView1'})
        if not table:
            return JSONResponse(
                content={"error": "Table not found in the response"},
                status_code=404
            )

        # Get all rows except the header
        rows = table.find_all('tr')[1:]  # Skip header row

        # Parse table data
        lottery_results = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 5:  # Ensure we have all columns
                # Remove extra spaces and strip whitespace
                combinations = cols[1].text.strip().replace(' ', '')
                jackpot = cols[3].text.strip().replace(',', '')  # Remove commas from numbers

                result = {
                    "game": cols[0].text.strip(),
                    "combinations": combinations,
                    "draw_date": cols[2].text.strip(),
                    "jackpot": float(jackpot.replace('PHP', '').strip()),  # Convert to float
                    "winners": int(cols[4].text.strip())  # Convert to integer
                }
                lottery_results.append(result)

        return JSONResponse(content={
            "status": response.status_code,
            "count": len(lottery_results),
            "results": lottery_results
        })
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
