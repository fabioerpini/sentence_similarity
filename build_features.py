import numpy as np
from gensim.utils import chunkize
from torch.nn.functional import softmax
from tqdm import tqdm
from llama_cpp import Llama

import os
import pickle
from itertools import combinations

import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import pandas as pd
from sentence_similarity import preprocess, tokenize, \
    embed_from_words, cosine_similarity_from_embeddings, glove_model, w2v_model, fasttext_model, LSA_model, T5_model, \
    RoBERTa_model, T5_generative_model
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


# @click.command()
# @click.argument('project_dir', type=click.Path())
def main(project_dir):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('extracting item similarity')
    logger.info(f'loading data')
    with open(os.path.join(project_dir, 'data/processed/items.pkl'), 'rb') as f:
        items = pickle.load(f)
    # responses = pd.read_pickle(os.path.join(project_dir, 'data/processed/responses.pkl'))
    # responses_factorized = pd.DataFrame({c: pd.factorize(responses[c])[0] for c in responses.columns})
    # responses_corr_spearman = responses_factorized.corr('spearman')
    # responses_corr_spearman.to_csv(os.path.join(project_dir, 'data/processed/response_spearman_correlation.csv'))
    # responses_corr_kendall = responses_factorized.corr('kendall')
    # responses_corr_kendall.to_csv(os.path.join(project_dir, 'data/processed/response_kendall_correlation.csv'))
    #
    # print(items, responses)

    item_df = pd.DataFrame(items.items(), columns=['code', 'item']).set_index('code')
    item_df['tokens'] = item_df.item.apply(preprocess).apply(tokenize)

    # # embed sentences via words
    # mean_word_embedding_cosine_similarities = dict()
    # word_embedding_wmd = dict()
    #
    # logger.info(f'loading models')
    # model_ft = fasttext_model()
    # model_w2v = w2v_model()
    # model_glove = glove_model()
    #
    # for model_name, model in dict(model_ft=model_ft, model_w2v=model_w2v, model_glove=model_glove).items():
    #     logger.info(f'computing for model {model_name}')
    #     item_df[f'{model_name}_token_embeddings'] = item_df.tokens.apply(
    #         lambda x: model[[xx for xx in x if xx in model.key_to_index]])
    #
    #     item_df[f'{model_name}_mean_word_embedding'] = item_df[f'{model_name}_token_embeddings'].apply(embed_from_words)
    #     mean_word_embedding_cosine_similarities[model_name] = pd.DataFrame(cosine_similarity_from_embeddings(
    #         item_df[f'{model_name}_mean_word_embedding']), index=item_df.index.values, columns=item_df.index.values)
    #     # mean_word_embedding_cosine_similarities[model_name] = cosine_similarity_from_embeddings(
    #     #     item_df[f'{model_name}_mean_word_embedding'].values)
    #     wmd = list()
    #     for q1, q2 in combinations(item_df.index, 2):
    #         dist = model.wmdistance([xx for xx in item_df.loc[q1, 'tokens'] if xx in model.key_to_index],
    #                                 [xx for xx in item_df.loc[q2, 'tokens'] if xx in model.key_to_index])
    #         wmd.append([q1, q2, dist])
    #         wmd.append([q2, q1, dist])
    #     wmd_df = pd.DataFrame(wmd).pivot(index=0, columns=1).fillna(0)
    #     wmd_df.columns = [i[1] for i in wmd_df.columns]
    #     wmd_df.index = [i for i in wmd_df.index]
    #     word_embedding_wmd[model_name] = wmd_df
    # for model_name, mean_word_embedding_cosine_similarity in mean_word_embedding_cosine_similarities.items():
    #     mean_word_embedding_cosine_similarity.to_csv(
    #         os.path.join(project_dir, f'data/processed/mean_word_embedding_cosine_similarity_{model_name}.csv'))
    # for model_name, wmd in word_embedding_wmd.items():
    #     wmd.to_csv(os.path.join(project_dir, f'data/processed/wmd_{model_name}.csv'))
    #
    # logger.info(f'computing sentence embedding similarity')
    # sentence_embedding_cosine_similarities = dict()
    # model_name = 'lsa_model'
    # model = LSA_model()
    # item_df[f'{model_name}_sentence_embedding'] = item_df.item.apply(lambda x: model.transform([x])[0])
    # sentence_embedding_cosine_similarities[model_name] = pd.DataFrame(cosine_similarity_from_embeddings(
    #     item_df[f'{model_name}_sentence_embedding']), index=item_df.index.values, columns=item_df.index.values)
    #
    # for model_name, model in (('sentence-t5-base', T5_model()), ('stsb-roberta-base', RoBERTa_model())):
    #     item_df[f'{model_name}_sentence_embedding'] = item_df.item.apply(model.encode)
    #     sentence_embedding_cosine_similarities[model_name] = pd.DataFrame(cosine_similarity_from_embeddings(
    #         item_df[f'{model_name}_sentence_embedding']), index=item_df.index.values, columns=item_df.index.values)
    # for model_name, sentence_embedding_cosine_similarity in sentence_embedding_cosine_similarities.items():
    #     sentence_embedding_cosine_similarity.to_csv(
    #         os.path.join(project_dir, f'data/processed/sentence_embedding_cosine_similarity_{model_name}.csv'))
    # item_df.to_csv(os.path.join(project_dir, f'data/processed/item_df.csv'))
    # item_df.to_pickle(os.path.join(project_dir, f'data/processed/item_df.pkl'))
    #
    # logger.info(f'computing sts')
    # model, tokenizer = T5_generative_model()
    #
    # sts = list()
    # for q1, q2 in combinations(item_df.index, 2):
    #     inputs = tokenizer(f"stsb sentence1:{items[q1]} sentence2:{items[q2]}", return_tensors="pt")
    #     outputs = model.generate(**inputs)
    #     response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    #     sts.append([q1, q2, response])
    #     sts.append([q2, q1, response])
    # sts_comparisons = pd.DataFrame(sts).pivot(index=0, columns=1)
    # sts_comparisons.columns = [i[1] for i in sts_comparisons.columns]
    # sts_comparisons.index = [i for i in sts_comparisons.index]
    #
    # sts_comparisons.to_csv(os.path.join(project_dir, f'data/processed/sts_comparisons.csv'))
    #
    # logger.info(f'computing nli')

    def all_pairs(lst):
        for i in lst:
            for j in lst:
                yield i, j

    # nli = list()
    # for q1, q2 in all_pairs(item_df.index):
    #     inputs = tokenizer(f"qnli sentence1:{items[q1]} sentence2:{items[q2]}", return_tensors="pt")
    #     outputs = model.generate(**inputs)
    #     response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    #     nli.append([q1, q2, response])
    # nli_comparisons = pd.DataFrame(nli).pivot(index=0, columns=1).fillna('entailment')
    # nli_comparisons.columns = [i[1] for i in nli_comparisons.columns]
    # nli_comparisons.index = [i for i in nli_comparisons.index]
    #
    # nli_comparisons.to_csv(os.path.join(project_dir, f'data/processed/nli_comparisons.csv'))

    llm = Llama(model_path="../../mistral-7b-instruct-v0.2.Q4_K_M.gguf", chat_format="llama-2",
                n_gpu_layers=-1,
                # verbose=False
                )
    for same_response in [True, False]:
        results_mistral = list()
        item_name_pairs = list()
        for q1, q2 in tqdm(all_pairs(item_df.index)):
            if q1 == q2:
                continue
            item_name_pairs.append((q1, q2))
            if same_response:
                prompt = f'<s>[INST] You rated, on a scale 1 to 10, how likely is it that one person would answer similarly to the following two questions. [Q1]"{items[q1]}"[/Q1] [Q2]"{items[q2]}"[/Q2] The number that corresponds to that likelihood is [/INST]'
            else:
                prompt = f'<s>[INST] You rated, on a scale 1 to 10, how likely is it that one person would give opposite answers to the following two questions. [Q1]"{items[q1]}"[/Q1] [Q2]"{items[q2]}"[/Q2] The number that corresponds to that likelihood is [/INST]'
            with torch.no_grad():
                # print(prompt)
                output = llm(
                    prompt,
                    temperature=.1,
                    max_tokens=2,
                )
                res = output['choices'][0]['text']
                results_mistral.append(res)
        df_mistral = pd.DataFrame(
            zip(map(lambda x: int(x) if x.strip().isnumeric() else x, results_mistral), (i[0] for i in item_name_pairs),
                (i[1] for i in item_name_pairs)), columns=['score', 'q1', 'q2'])
        df_mistral.loc[df_mistral.score.apply(lambda x: (not isinstance(x, int)) and (
                'low' in x)), 'score'] = 0  # cases where it's a paraphrasis of "low likelihood"
        df_mistral.loc[df_mistral.score.apply(
            lambda x: not isinstance(x, int)), 'score'] = 5  # remaining cases, hard to tell: give middling answer
        df_mistral = df_mistral.pivot_table(values='score', index='q1', columns='q2').fillna(10 if same_response else 0)
        df_mistral /= 10
        df_mistral.to_csv(os.path.join(project_dir,
                                       f'data/processed/mistral_{"same" if same_response else "opposite"}_response_likelihood.csv'))

    # item_name_pairs = list()
    # item_pairs = list()
    #
    # for q1_name, q1 in items.items():
    #     for q2_name, q2 in items.items():
    #         if q1_name != q2_name:
    #             item_pairs.append((q1, q2))
    #             item_name_pairs.append((q1_name, q2_name))
    # model = AutoModelForSequenceClassification.from_pretrained('cross-encoder/nli-deberta-v3-large')
    # tokenizer = AutoTokenizer.from_pretrained('cross-encoder/nli-deberta-v3-large')
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # print(device)
    # model.eval()
    # model = model.to(device)
    # scores = list()
    # for batch in chunkize(item_pairs, 100):
    #     features = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
    #     features = features.to(device)
    #
    #     with torch.no_grad():
    #         scores.append(model(**features).logits)
    #         # labels = [label_mapping[score_max] for score_max in scores.argmax(dim=1)]
    # scores_ = np.vstack([softmax(s.cpu(), 1) for s in scores])
    # contradiction, entailment, neutral = (scores_[:, i] for i in range(3))
    # torch.cuda.empty_cache()
    # df_contradiction = pd.DataFrame(
    #     zip(contradiction, (i[0] for i in item_name_pairs), (i[1] for i in item_name_pairs)),
    #     columns=['score', 'q1', 'q2'])
    # df_contradiction = df_contradiction.pivot_table(values='score', index='q1', columns='q2').fillna(0)
    # df_contradiction.to_csv(os.path.join(project_dir, 'data/processed/nli_comparison_contradiction.csv'))
    #
    # df_neutral = pd.DataFrame(zip(neutral, (i[0] for i in item_name_pairs), (i[1] for i in item_name_pairs)),
    #                           columns=['score', 'q1', 'q2'])
    # df_neutral = df_neutral.pivot_table(values='score', index='q1', columns='q2').fillna(0)
    # df_neutral.to_csv(os.path.join(project_dir, 'data/processed/nli_comparison_neutral.csv'))
    #
    # df_entailment = pd.DataFrame(zip(entailment, (i[0] for i in item_name_pairs), (i[1] for i in item_name_pairs)),
    #                              columns=['score', 'q1', 'q2'])
    # df_entailment = df_entailment.pivot_table(values='score', index='q1', columns='q2').fillna(1)
    # df_entailment.to_csv(os.path.join(project_dir, 'data/processed/nli_comparison_entailment.csv'))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main(project_dir)
