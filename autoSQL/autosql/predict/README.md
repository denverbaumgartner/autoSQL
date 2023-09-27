# SQLPredict

## Inferences

| Date     | Avg. Inference Time (1/100) | Model             | Data                                                   | 
|----------|-----------------------------|-------------------|--------------------------------------------------------|
| 09/27/23 | 1.80s/request               | `gpt-3.5-turbo`   | [rich_testing_subset][rich_testing_subset] (0, 100)    |
| 09/27/23 | 1.54s/request               | `gpt-3.5-turbo`   | [rich_testing_subset][rich_testing_subset] (100, 200)  |
| 09/27/23 | 1.38s/request               | `gpt-3.5-turbo`   | [rich_testing_subset][rich_testing_subset] (200, 300)  |
| 09/27/23 | 3.08s/request               | `llama-2-13b-sql` | [rich_testing_subset][rich_testing_subset] (0, 100)    |
| 09/27/23 | 2.45s/request               | `llama-2-13b-sql` | [rich_testing_subset][rich_testing_subset] (100, 200)  |
| 09/27/23 | 1.38s/request               | `llama-2-13b-sql` | [rich_testing_subset][rich_testing_subset] (200, 300)  |

[gpt-3.5-turbo]: 
[llama-2-13b-sql]: 
[rich_testing_subset]: https://huggingface.co/datasets/alagaesia/auto-sql-create-context/blob/main/rich_testing_subset_llama_13b_1_0_0_inferences.zip