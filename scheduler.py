from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import httpx

async def call_xml_endpoint():
    """
    Asynchronously call the XML endpoint to fetch XML feeds.

    This function uses an asynchronous HTTP client to send a GET request to the XML endpoint.
    It logs a success message if the request is successful, otherwise logs an error message
    with the status code or exception details.

    Raises:
        Exception: If there is an error during the HTTP request.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Send a GET request to the XML endpoint
            response = await client.get("http://localhost:8000/xml/")
            if response.status_code == 200:
                print("Successfully fetched XML feeds")
            else:
                print(f"Error fetching XML feeds: {response.status_code}")
        except Exception as e:
            print(f"Error calling XML endpoint: {str(e)}")

def init_scheduler():
    """
    Initialize and start the asynchronous scheduler for background tasks.

    This function sets up an AsyncIOScheduler to run the `call_xml_endpoint` function
    daily at 11:59 PM. The job is configured to replace any existing job with the same ID.

    Returns:
        AsyncIOScheduler: The initialized and started scheduler instance.
    """
    scheduler = AsyncIOScheduler()

    # Schedule the `call_xml_endpoint` job to run daily at 11:59 PM
    scheduler.add_job(
        call_xml_endpoint,
        CronTrigger(hour=23, minute=59),
        id="fetch_xml_feeds",
        name="Fetch XML feeds daily",
        replace_existing=True,  # Replace any existing job with the same ID
    )

    # Start the scheduler to begin executing scheduled jobs
    scheduler.start()
    return scheduler
