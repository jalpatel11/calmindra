import os
import sys
import asyncio
import hashlib

# Ensure backend folder is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.vertex_client import VertexClient
from app.services.neo4j_client import Neo4jClient

# Sample Cognitive Behavioral Therapy (CBT) & Mental Health Resources
SEEDED_RESOURCES = [
    {
        "title": "Coping with Anxiety and Panic Attacks",
        "content": (
            "When experiencing high anxiety or a panic attack, practice the 5-4-3-2-1 grounding technique. "
            "Acknowledge: 5 things you can see around you, 4 things you can physically touch, 3 things you can hear, "
            "2 things you can smell, and 1 thing you can taste. This shifts focus from internal panic to external reality."
        )
    },
    {
        "title": "Box Breathing for Stress Reduction",
        "content": (
            "Box breathing is a powerful vagus nerve stimulant for stress relief. "
            "Inhale deeply through the nose for a count of 4. Hold the breath for a count of 4. "
            "Exhale slowly through the mouth for a count of 4. Hold empty for a count of 4. "
            "Repeat this cycle 4 to 5 times to activate the parasympathetic nervous system and lower heart rate."
        )
    },
    {
        "title": "Identifying and Challenging Cognitive Distortions",
        "content": (
            "Cognitive distortions are exaggerated or irrational thought patterns. Common examples include: "
            "All-or-Nothing Thinking (viewing things as absolute black-and-white), Catastrophizing (expecting the worst outcome), "
            "and Mind Reading (assuming others think negatively of you). Challenge these by asking: "
            "'What is the objective evidence for this thought? Are there alternative, more realistic explanations?'"
        )
    },
    {
        "title": "Managing Negative Thought Loops",
        "content": (
            "When trapped in rumination or a negative thought loop, use the 'Thought Stopping and Redirection' method. "
            "Recognize the loop, mentally say 'Stop!', and actively redirect your attention to a neutral or positive task. "
            "Alternatively, allocate a dedicated 15-minute 'Worry Time' earlier in the day, so when worries arise later, "
            "you can postpone them by telling yourself: 'I will deal with this during my scheduled worry time.'"
        )
    },
    {
        "title": "Improving Sleep Hygiene and Insomnia",
        "content": (
            "Good sleep hygiene is essential for mental health. "
            "Establish a consistent wake-up time. Keep the bedroom cool, dark, and quiet. "
            "Avoid screens (blue light) at least 60 minutes before bed. "
            "If you cannot sleep after 20 minutes, get out of bed and do a quiet, non-stimulating activity "
            "in dim light until you feel sleepy. This prevents the bed from becoming associated with frustration."
        )
    },
    {
        "title": "Behavioral Activation for Depression",
        "content": (
            "Behavioral activation involves scheduling activities that bring a sense of pleasure or achievement. "
            "When experiencing low mood, motivation follows action, not the other way around. "
            "Start with small, manageable goals: take a 5-minute walk, send a brief message to a friend, "
            "or clean one surface in your room. Celebrate these minor victories to break the cycle of withdrawal."
        )
    },
    {
        "title": "Practicing Mindfulness Meditation",
        "content": (
            "Mindfulness is the practice of focusing awareness on the present moment while non-judgmentally acknowledging "
            "feelings and thoughts. Try a basic breathing anchor: sit comfortably, close your eyes, and focus entirely "
            "on the physical sensation of breathing (the expansion of the chest or the air entering the nostrils). "
            "When your mind wanders—which it naturally will—simply note it and gently guide it back to the breath."
        )
    },
    {
        "title": "The Circle of Control",
        "content": (
            "When feeling overwhelmed by life circumstances, draw a circle. "
            "Inside the circle, write things you have direct control over (e.g., your actions, your routine, how you respond). "
            "Outside the circle, write things you cannot control (e.g., other people's opinions, global events, the past). "
            "Focus your emotional energy strictly on the items inside the circle to reduce feelings of helplessness."
        )
    }
]

async def main():
    print("=== Starting Cloud DB Ingestion & Seeding ===")
    
    # 1. Initialize services
    vertex = VertexClient()
    neo4j_client = Neo4jClient()
    
    try:
        # Initialize Database connection & index
        await neo4j_client.initialize_database()
        
        # 2. Process and Ingest resources
        for index, item in enumerate(SEEDED_RESOURCES):
            content = f"Title: {item['title']}\nContent: {item['content']}"
            doc_id = hashlib.md5(content.encode("utf-8")).hexdigest()
            
            print(f"[{index + 1}/{len(SEEDED_RESOURCES)}] Embedding: '{item['title']}'...")
            
            # Generate Vertex AI embedding
            embedding = await vertex.get_embedding(content)
            
            # Save document to Neo4j
            await neo4j_client.ingest_document(
                doc_id=doc_id,
                content=content,
                embedding=embedding
            )
            print(f" -> Successfully ingested into Neo4j with ID {doc_id}.")
            
        print("=== Database Ingestion Completed Successfully ===")
    except Exception as e:
        print(f"Error seeding database: {e}", file=sys.stderr)
    finally:
        await neo4j_client.close()

if __name__ == "__main__":
    asyncio.run(main())
