import json

DB = {
    "organizations": [
      {
        "id": "org_abc123",
        "name": "Acme Corp",
        "created_at": "2023-01-15T10:00:00Z",
        "subscription_plan": {
          "id": "plan_pro",
          "name": "Pro Plan",
          "price": 25.00,
          "currency": "USD",
          "features": [
            "unlimited_projects",
            "priority_support",
            "daily_backups",
            "branching_enabled",
            "edge_functions_enabled"
          ]
        }
      },
      {
        "id": "org_xyz789",
        "name": "Innovate Solutions",
        "created_at": "2022-05-20T14:30:00Z",
        "subscription_plan": {
          "id": "plan_free",
          "name": "Free Tier",
          "price": 0.00,
          "currency": "USD",
          "features": [
            "limited_projects",
            "community_support"
          ]
        }
      }
    ],
    "projects": [
      {
        "id": "proj_1a2b3c",
        "name": "Acme CRM",
        "organization_id": "org_abc123",
        "region": "us-east-1",
        "status": "ACTIVE",
        "created_at": "2023-02-01T09:15:00Z",
        "version": "PostgreSQL 15"
      },
      {
        "id": "proj_4d5e6f",
        "name": "Innovate Analytics",
        "organization_id": "org_xyz789",
        "region": "eu-central-1",
        "status": "ACTIVE",
        "created_at": "2022-06-10T11:00:00Z",
        "version": "PostgreSQL 14"
      },
      {
        "id": "proj_7g8h9i",
        "name": "Acme Mobile App Backend",
        "organization_id": "org_abc123",
        "region": "ap-southeast-1",
        "status": "INITIALIZING",
        "created_at": "2023-03-20T16:45:00Z",
        "version": None
      }
    ],
    "tables": {
      "proj_1a2b3c": [
        {
          "name": "users",
          "schema": "public",
          "comment": "Stores user data",
          "columns": [
            {
              "name": "id",
              "data_type": "uuid",
              "is_nullable": False,
              "default_value": "uuid_generate_v4()"
            },
            {
              "name": "email",
              "data_type": "text",
              "is_nullable": False,
              "default_value": None
            },
            {
              "name": "created_at",
              "data_type": "timestamp with time zone",
              "is_nullable": False,
              "default_value": "now()"
            }
          ],
          "primary_keys": [
            { "name": "id" }
          ],
          "relationships": []
        },
        {
          "name": "posts",
          "schema": "public",
          "comment": "Blog posts",
          "columns": [
            {
              "name": "id",
              "data_type": "uuid",
              "is_nullable": False,
              "default_value": "uuid_generate_v4()"
            },
            {
              "name": "user_id",
              "data_type": "uuid",
              "is_nullable": False,
              "default_value": None
            },
            {
              "name": "title",
              "data_type": "text",
              "is_nullable": False,
              "default_value": None
            },
            {
              "name": "content",
              "data_type": "text",
              "is_nullable": True,
              "default_value": None
            },
            {
              "name": "published_at",
              "data_type": "timestamp with time zone",
              "is_nullable": True,
              "default_value": None
            }
          ],
          "primary_keys": [
            { "name": "id" }
          ],
          "relationships": [
            {
              "constraint_name": "fk_user_id",
              "source_schema": "public",
              "source_table_name": "posts",
              "source_column_name": "user_id",
              "target_table_schema": "public",
              "target_table_name": "users",
              "target_column_name": "id"
            }
          ]
        }
      ],
      "proj_4d5e6f": [
        {
          "name": "customers",
          "schema": "analytics",
          "comment": "Customer data for analytics",
          "columns": [
            { "name": "customer_id", "data_type": "integer", "is_nullable": False, "default_value": None },
            { "name": "name", "data_type": "text", "is_nullable": False, "default_value": None },
            { "name": "segment", "data_type": "text", "is_nullable": True, "default_value": "'new'" }
          ],
          "primary_keys": [
            { "name": "customer_id" }
          ],
          "relationships": []
        }
      ]
    },
    "extensions": {
      "proj_1a2b3c": [
        {
          "name": "uuid-ossp",
          "schema": "extensions",
          "version": "1.1",
          "description": "generate universally unique identifiers (UUIDs)"
        },
        {
          "name": "pg_stat_statements",
          "schema": "public",
          "version": "1.9",
          "description": "track execution statistics of all SQL statements executed"
        }
      ],
      "proj_4d5e6f": [
        {
          "name": "pg_cron",
          "schema": "extensions",
          "version": "1.5",
          "description": "Job scheduler for PostgreSQL"
        }
      ]
    },
    "migrations": {
      "proj_1a2b3c": [
        {
          "version": "20230201090000",
          "name": "init_schema",
          "status": "applied",
          "applied_at": "2023-02-01T09:00:05Z",
          "query": "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"; CREATE TABLE public.users (id uuid PRIMARY KEY DEFAULT uuid_generate_v4(), email text NOT NULL, created_at timestamptz DEFAULT now());"
        },
        {
          "version": "20230205103000",
          "name": "create_posts_table",
          "status": "applied",
          "applied_at": "2023-02-05T10:30:10Z",
          "query": "CREATE TABLE public.posts (id uuid PRIMARY KEY DEFAULT uuid_generate_v4(), user_id uuid NOT NULL REFERENCES public.users(id), title text NOT NULL, content text, published_at timestamptz);"
        }
      ],
      "proj_4d5e6f": [
        {
          "version": "20220610105000",
          "name": "create_customers_table",
          "status": "applied",
          "applied_at": "2022-06-10T10:50:05Z",
          "query": "CREATE SCHEMA analytics; CREATE TABLE analytics.customers (customer_id SERIAL PRIMARY KEY, name text NOT NULL, segment text DEFAULT 'new');"
        }
      ]
    },
    "edge_functions": {
      "proj_1a2b3c": [
        {
          "id": "func_greet_user",
          "slug": "greet-user",
          "name": "Greet User Function",
          "version": "v1.0.1",
          "status": "ACTIVE",
          "created_at": "2023-02-10T11:00:00Z",
          "updated_at": "2023-02-15T14:22:00Z",
          "entrypoint_path": "index.ts",
          "import_map_path": None,
          "files": [
            {
              "name": "index.ts",
              "content": "import \"jsr:@supabase/functions-js/edge-runtime.d.ts\";\nDeno.serve(async (req: Request) => {\n  const name = new URL(req.url).searchParams.get('name') || 'world';\n  return new Response(`Hello, ${name}!`, { headers: { 'Content-Type': 'text/plain' } });\n});"
            }
          ]
        }
      ]
    },
    "branches": {
      "proj_1a2b3c": [
        {
          "id": "branch_dev_crm",
          "name": "develop-crm",
          "parent_project_id": "proj_1a2b3c",
          "branch_project_id": "proj_crmdev_db",
          "status": "ACTIVE",
          "created_at": "2023-03-01T08:00:00Z",
          "last_activity_at": "2023-03-22T09:30:00Z"
        }
      ]
    },
    "costs": {
      "conf_proj_5f7g8h": {
        "type": "project",
        "amount": 25.00,
        "currency": "USD",
        "recurrence": "monthly",
        "description": "Cost for a new Pro Plan project",
        "confirmation_id": "conf_proj_5f7g8h"
      }
    },
    "unconfirmed_costs": {
      "quote_proj_temp": {
        "type": "project",
        "amount": 25.00,
        "currency": "USD",
        "recurrence": "monthly",
        "description": "Quote for a new project in Acme Corp."
      }
    },
    "project_urls": {
      "proj_1a2b3c": "https://abc123crm.supabase.co",
      "proj_4d5e6f": "https://xyz789analytics.supabase.co"
    },
    "project_anon_keys": {
      "proj_1a2b3c": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InByb2oxYTJiM2MiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY3MzcxMzYwMCwiZXhwIjoxODMwNTcxMjAwfQ.example_anon_key_1",
      "proj_4d5e6f": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InByb2o0ZDVlNmYiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY3MzcxMzYwMCwiZXhwIjoxODMwNTcxMjAwfQ.example_anon_key_2"
    },
    "project_ts_types": {
      "proj_1a2b3c": "export type Json = | string | number | boolean | null | { [key: string]: Json | undefined } | Json[]\n\nexport type Database = {\n  public: {\n    Tables: {\n      users: {\n        Row: {\n          id: string\n          email: string\n          created_at: string\n        }\n        Insert: {\n          id?: string\n          email: string\n          created_at?: string\n        }\n        Update: {\n          id?: string\n          email?: string\n          created_at?: string\n        }\n        Relationships: []\n      }\n      posts: {\n        Row: {\n          id: string\n          user_id: string\n          title: string\n          content: string | null\n          published_at: string | null\n        }\n        Insert: {\n          id?: string\n          user_id: string\n          title: string\n          content?: string | null\n          published_at?: string | null\n        }\n        Update: {\n          id?: string\n          user_id?: string\n          title?: string\n          content?: string | null\n          published_at?: string | null\n        }\n        Relationships: [\n          { foreignKeyName: 'fk_user_id'; columns: ['user_id']; referencedRelation: 'users'; referencedColumns: ['id'] }\n        ]\n      }\n    }\n    Views: {}\n    Functions: {}\n    Enums: {}\n    CompositeTypes: {}\n  }\n}\n"
    },
    "logs": {
      "proj_1a2b3c": {
        "api": [
          {
            "timestamp": "2025-05-22T15:28:00Z",
            "level": "INFO",
            "message": "API request: GET /rest/v1/users",
            "metadata": { "request_id": "req_12345", "ip_address": "192.168.1.100" }
          },
          {
            "timestamp": "2025-05-22T15:28:15Z",
            "level": "WARN",
            "message": "Potential slow query detected: SELECT * FROM posts WHERE user_id = 'user_slow';",
            "metadata": { "query_time_ms": 1500 }
          }
        ],
        "postgres": [
          {
            "timestamp": "2025-05-22T15:28:30Z",
            "level": "DEBUG",
            "message": "DB connection established for user 'supabase_admin'",
            "metadata": {}
          }
        ]
      }
    }
  }


def save_state(filepath: str) -> None:
    with open(filepath, "w") as f:
        json.dump(DB, f)


def load_state(filepath: str, error_config_path: str = "./error_config.json", error_definitions_path: str = "./error_definitions.json") -> object:
    global DB
    with open(filepath, "r") as f:
        state = json.load(f)
    # Instead of reassigning DB, update it in place:
    DB.clear()
    DB.update(state)