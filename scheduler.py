from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import httpx

async def call_xml_endpoint():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/xml/")
            if response.status_code == 200:
                print("Successfully fetched XML feeds")
            else:
                print(f"Error fetching XML feeds: {response.status_code}")
        except Exception as e:
            print(f"Error calling XML endpoint: {str(e)}")

def init_scheduler():
    scheduler = AsyncIOScheduler()
    
    # Schedule the job to run at 11:59 PM every day
    scheduler.add_job(
        call_xml_endpoint,
        CronTrigger(hour=23, minute=59),
        id="fetch_xml_feeds",
        name="Fetch XML feeds daily",
        replace_existing=True
    )
    
    scheduler.start()
    return scheduler