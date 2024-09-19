from neo4j_graph import Graph

def initialise_neo4j(graph):
    cypher_schema = [
        "CREATE CONSTRAINT sectionKey IF NOT EXISTS FOR (c:Section) REQUIRE (c.key) IS UNIQUE;",
        "CREATE CONSTRAINT chunkKey IF NOT EXISTS FOR (c:Chunk) REQUIRE (c.key) IS UNIQUE;",
        "CREATE CONSTRAINT documentKey IF NOT EXISTS FOR (c:Document) REQUIRE (c.url_hash) IS UNIQUE;",
        "CALL db.index.vector.createNodeIndex('chunkVectorIndex', 'Embedding', 'value', 1536, 'COSINE');"
    ]

    for cypher in cypher_schema:
        graph.query(cypher)

def insert_document(graph, document):

    url = document.metadata['source']
    url_hashed = hash(url)
    
    cypher = """
            MERGE (d:Document {urlHash: $doc_url_hash}) 
            ON CREATE SET d.url = $doc_url 
            RETURN d;
            """

    response = graph.query(cypher, params={"doc_url_hash": url_hashed, "doc_url": url})

def insert_sections(graph, doc_id, chunks):
    cypher = """
            MERGE (p:Section {key: $doc_id+'|'+$section_id}) 
            ON CREATE SET p.section_id = $section_id, p.title = $title 
            RETURN p;
            """

    for chunk in chunks: 
        for section in chunk.metadata:
            secion_id = hash(section)

            response = graph.query(cypher, params={"doc_id": doc_id, "section_id": section_id, "title": section})

def derive_sections(graph, document):
    cypher_create_from_chunks = """
            MATCH (c:Chunk)
            MERGE (s:Section {id: coalesce(c.header4, c.header3, c.header2, c.header1) } )
            SET s.header1 = c.header1
            , s.header2 = c.header2
            , s.header3 = c.header3
            , s.level = CASE WHEN c.header4 IS NOT NULL THEN 4
                             WHEN c.header3 IS NOT NULL THEN 3
                             WHEN c.header2 IS NOT NULL THEN 2
                             WHEN c.header1 IS NOT NULL THEN 1
                        END 
            , s.text = coalesce(c.header4, c.header3, c.header2, c.header1)   
            MERGE (s)-[newRel:CONTAINS]->(c)
            """

    cypher_create_other_sections = """
            MATCH (e:Section)
            WHERE e.level = $level_to_create+1
            WITH e, CASE WHEN $level_to_create = 1 THEN e.header1
                    WHEN $level_to_create = 2 THEN e.header2
                    WHEN $level_to_create = 3 THEN e.header3
                END as text
            MERGE (s:Section {id: text} )
            set s.header1 = e.header1
                , s.header2 = e.header2
                , s.level = $level_to_create
                , s.text = text    
            MERGE (s)-[newRel:CONTAINS]->(e)
            """

    cypher_link_to_document = """
            MATCH (s:Section), (d:Document)
            WHERE s.level = 1 AND d.urlHash = $url_hash
            MERGE (d)-[newRel:CONTAINS]->(s)
            """

    response = graph.query(cypher_create_from_chunks)

    response = graph.query(cypher_create_other_sections, params={"level_to_create":3})
    response = graph.query(cypher_create_other_sections, params={"level_to_create":2})
    response = graph.query(cypher_create_other_sections, params={"level_to_create":1})

    url = document.metadata['source']
    url_hashed = hash(url)
    response = graph.query(cypher_link_to_document, params={"url_hash": url_hashed})

def insert_chunks(graph, doc_id, section_id, chunks):

    cypher = """
            MERGE (c:Chunk {key: $doc_id+'|'+$section_id+'|'+$chunk_id}) 
            ON CREATE SET c.text = $text, c += $metadata
            RETURN c;

            """

    for i, chunk in enumerate(chunks):
        response = graph.query(cypher, params={"doc_id": doc_id, "section_id": section_id, "chunk_id": i, "text": chunk.page_content, "metadata": chunk.metadata})

