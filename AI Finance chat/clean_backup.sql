--
-- PostgreSQL database dump
--

\restrict FCfZIWaSGQZGOWTUO7LyEhp61ndjfkaosX0scJ0g48YzRKPkrwq2ipgdj80iHMh

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    type text NOT NULL,
    amount numeric(15,2) NOT NULL,
    category_id integer,
    note text,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT transactions_amount_check CHECK ((amount > (0)::numeric)),
    CONSTRAINT transactions_type_check CHECK ((type = ANY (ARRAY['sale'::text, 'expense'::text])))
);


--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.categories (id, name) VALUES (1, 'electricity');
INSERT INTO public.categories (id, name) VALUES (2, 'rent');
INSERT INTO public.categories (id, name) VALUES (3, 'salaries');
INSERT INTO public.categories (id, name) VALUES (4, 'supplies');
INSERT INTO public.categories (id, name) VALUES (5, 'food');
INSERT INTO public.categories (id, name) VALUES (6, 'transport');
INSERT INTO public.categories (id, name) VALUES (7, 'marketing');
INSERT INTO public.categories (id, name) VALUES (8, 'other');
INSERT INTO public.categories (id, name) VALUES (9, 'product_sale');
INSERT INTO public.categories (id, name) VALUES (10, 'service_sale');


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (1, 'expense', 500.00, 8, NULL, '2026-04-06 13:17:28.127544');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (2, 'expense', 123.45, 5, 'PostgreSQL test', '2026-04-06 13:23:07.064496');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (3, 'sale', 2000.00, 9, NULL, '2026-04-07 12:59:54.661235');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (4, 'sale', 500.00, 9, NULL, '2026-04-04 06:14:56');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (5, 'expense', 200.00, 1, NULL, '2026-04-04 06:15:53');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (6, 'expense', 1.00, 1, NULL, '2026-04-04 06:18:48');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (7, 'sale', 5000.00, 9, NULL, '2026-04-04 06:33:03');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (8, 'expense', 300.00, 5, NULL, '2026-04-04 06:33:19');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (9, 'expense', 99.00, 5, NULL, '2026-04-04 06:34:21');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (10, 'sale', 2000.00, 9, NULL, '2026-04-04 07:11:56');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (11, 'expense', 1500.00, 8, NULL, '2026-04-04 07:12:40');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (12, 'expense', 200.00, 8, NULL, '2026-04-04 07:14:28');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (13, 'sale', 2200.00, 9, NULL, '2026-04-04 07:42:57');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (14, 'expense', 500.00, 1, NULL, '2026-04-06 07:52:45');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (15, 'sale', 5000.00, 9, NULL, '2026-04-06 07:54:09');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (16, 'expense', 500.00, 1, NULL, '2026-04-06 08:00:02');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (17, 'expense', 500.00, 1, NULL, '2026-04-06 08:01:55');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (18, 'expense', 500.00, 1, NULL, '2026-04-07 13:05:13.319654');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (19, 'expense', 5100.00, 1, NULL, '2026-04-07 13:11:07.252947');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (20, 'sale', 500.00, 9, NULL, '2026-04-07 13:17:34.8277');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (21, 'expense', 500.00, 1, NULL, '2026-04-07 14:35:03.660887');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (22, 'sale', 3000.00, 9, NULL, '2026-04-07 14:35:48.678839');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (23, 'expense', 500.00, 1, NULL, '2026-04-07 14:36:30.85267');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (24, 'expense', 500.00, 1, NULL, '2026-04-07 16:20:29.096464');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (25, 'sale', 500.00, 9, NULL, '2026-04-09 12:57:08.27852');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (26, 'expense', 500.00, 2, NULL, '2026-04-09 12:57:36.222578');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (27, 'sale', 200.00, 9, NULL, '2026-04-09 13:00:43.56801');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (28, 'expense', 2200.00, 2, NULL, '2026-04-09 13:01:14.40597');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (29, 'expense', 300.00, 5, NULL, '2026-04-09 13:01:35.394899');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (30, 'sale', 2200.00, 9, NULL, '2026-04-09 13:02:44.207483');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (31, 'sale', 2000.00, 9, NULL, '2026-04-09 13:03:08.372324');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (32, 'expense', 200.00, 5, NULL, '2026-04-09 13:03:42.578776');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (33, 'sale', 200.00, 9, NULL, '2026-04-09 13:04:14.236744');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (34, 'expense', 500.00, 5, NULL, '2026-04-09 13:06:29.130383');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (35, 'sale', 500.00, 9, NULL, '2026-04-09 13:09:05.629165');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (36, 'sale', 500.00, 9, NULL, '2026-04-09 13:09:43.003283');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (37, 'expense', 500.00, 1, NULL, '2026-04-10 15:03:56.177381');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (38, 'expense', 500.00, 1, NULL, '2026-04-10 15:13:20.758852');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (39, 'expense', 500.00, 1, NULL, '2026-04-10 15:13:34.977185');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (40, 'expense', 500.00, 1, NULL, '2026-04-10 15:13:35.894987');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (41, 'sale', 100.00, 9, NULL, '2026-04-10 15:13:59.530252');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (42, 'expense', 500.00, 1, NULL, '2026-04-10 15:41:37.028516');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (43, 'sale', 500.00, 9, NULL, '2026-04-10 15:43:27.223514');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (44, 'sale', 150.00, 9, NULL, '2026-04-10 15:52:35.13177');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (45, 'sale', 500.00, 9, NULL, '2026-04-10 16:02:58.719487');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (46, 'sale', 500.00, 9, NULL, '2026-04-10 16:13:42.326856');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (47, 'expense', 500.00, 1, NULL, '2026-04-10 16:17:40.570209');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (48, 'sale', 500.00, 9, NULL, '2026-04-10 16:18:07.226582');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (49, 'sale', 500.00, 9, NULL, '2026-04-10 16:19:46.300878');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (50, 'sale', 500.00, 9, NULL, '2026-04-10 16:23:19.894304');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (51, 'expense', 500.00, 2, NULL, '2026-04-10 16:25:55.273424');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (52, 'sale', 500.00, 9, NULL, '2026-04-10 16:29:13.137826');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (53, 'sale', 500.00, 9, NULL, '2026-04-10 16:29:41.613894');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (54, 'sale', 1502.00, 9, NULL, '2026-04-10 16:31:42.345025');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (55, 'expense', 500.00, 2, NULL, '2026-04-10 16:33:24.743132');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (56, 'sale', 500.00, 9, NULL, '2026-04-10 16:44:53.829501');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (57, 'expense', 500.00, 1, NULL, '2026-04-10 16:50:39.118359');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (58, 'expense', 13000.00, 8, NULL, '2026-04-10 16:55:09.956323');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (59, 'sale', 171.00, 9, NULL, '2026-04-10 17:22:49.463542');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (60, 'sale', 0.10, 9, NULL, '2026-04-10 17:23:29.589577');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (61, 'sale', 1.00, 9, NULL, '2026-04-10 17:24:02.959382');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (62, 'expense', 5001.00, 8, NULL, '2026-04-10 17:31:59.238268');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (63, 'sale', 5000.00, 9, NULL, '2026-04-11 15:57:09.619001');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (64, 'sale', 1050.00, 9, NULL, '2026-04-11 15:59:05.972');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (65, 'sale', 12050.00, 9, NULL, '2026-04-11 16:00:52.682954');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (66, 'sale', 200000.00, 9, NULL, '2026-04-11 16:03:39.332808');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (67, 'expense', 50000.00, 8, NULL, '2026-04-11 16:05:48.469515');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (68, 'expense', 500.00, 2, NULL, '2026-04-15 10:59:53.439296');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (69, 'sale', 4.00, 9, NULL, '2026-04-15 12:34:18.136434');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (70, 'expense', 10.00, 8, NULL, '2026-04-15 12:34:44.131936');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (71, 'sale', 500.00, 9, NULL, '2026-04-15 17:23:20.601793');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (72, 'expense', 500.00, 8, NULL, '2026-04-15 17:31:31.030747');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (73, 'sale', 500.00, 9, NULL, '2026-04-15 17:33:27.562355');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (74, 'expense', 1000.00, 8, NULL, '2026-04-15 17:33:55.542399');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (75, 'expense', 12.00, 1, NULL, '2026-04-15 17:36:14.468747');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (76, 'expense', 500.00, 1, NULL, '2026-04-18 12:54:45.122197');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (77, 'expense', 500.00, 1, NULL, '2026-04-18 12:56:30.968757');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (78, 'sale', 3000.00, 9, NULL, '2026-04-18 12:57:12.78742');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (79, 'sale', 500.00, 9, NULL, '2026-04-18 12:58:48.259052');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (80, 'expense', 5000.00, 5, NULL, '2026-04-18 12:59:09.760303');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (81, 'sale', 5000.00, 9, NULL, '2026-04-18 13:14:06.470353');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (82, 'expense', 500.00, 1, NULL, '2026-04-20 12:39:20.549872');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (83, 'expense', 500.00, 1, NULL, '2026-04-20 13:21:08.031453');
INSERT INTO public.transactions (id, type, amount, category_id, note, date) VALUES (84, 'expense', 500.00, 8, NULL, '2026-04-20 13:21:42.27644');


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_id_seq', 490, true);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.transactions_id_seq', 84, true);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- PostgreSQL database dump complete
--

\unrestrict FCfZIWaSGQZGOWTUO7LyEhp61ndjfkaosX0scJ0g48YzRKPkrwq2ipgdj80iHMh

