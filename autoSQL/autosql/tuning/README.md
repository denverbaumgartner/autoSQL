# Replicate Tuning

For a quick tutorial on fine-tuning language models (Llama-2) on Replicate, please see the [following](https://replicate.com/docs/guides/fine-tune-a-language-model). 

Requirements: 

- [ ] Register an account with Replicate [here](https://replicate.com/)
- [ ] Create a model instance to perform training on [here](https://replicate.com/create)
- [ ] Retrieve your authentification token [here](https://replicate.com/account/api-tokens)

`ngrok http 3000`

## Model Versions

| model_name  | base_model | model_url | train_date | train_time | train_data | test_data | hf_data |
|-------------|--------------------------|------------|-----------|------------|------------|------------|-----------|---------|
| llama-2-13b | [replicate][base_model_link] | [replicate][model_url_link] | 09/26/23  | 0sec      | [gist][train_data_link] | [gist][test_data_link] | [hf_repo][hf_repo_link] |

[base_model_link]: https://replicate.com/meta/llama-2-13b/versions/078d7a002387bd96d93b0302a4c03b3f15824b63104034bfa943c63a8f208c38
[model_url_link]: https://replicate.com/denverbaumgartner/llama-2-7b-sql
[train_data_link]: https://gist.githubusercontent.com/denverbaumgartner/ab65ea8d80dd1d7a49cb142c345ee8b3/raw/a6bae0b89b0cd6e3e3a8f00f55a67ff9bb1658e0/training_data_llama_13b_1_0_0.jsonl
[test_data_link]: https://gist.githubusercontent.com/denverbaumgartner/54d5522e9b6a4dbfb5ea3b24d2a682ae/raw/40ef986eab9a0332e0829ac484e1c04fc6189159/testing_data_llama_13b_1_0_0.jsonl
[hf_repo_link]: https://huggingface.co/datasets/alagaesia/auto-sql-create-context/tree/main

## Further Improvements: 
- [ ] enable direct publishing to hugging face hub 